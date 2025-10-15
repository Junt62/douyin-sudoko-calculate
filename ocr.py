import os
import cv2
import numpy as np
import pytesseract
import mss


def load_digit_templates(dir_path="templates"):
    templates = {}
    for d in range(10):
        p = os.path.join(dir_path, f"num{d+1}.png")
        img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"模板不存在: {p}")
        templates[str(d)] = img  # 不缩放
    return templates


def get_ocr_image(image, left, top, width, height):
    with mss.mss() as sct:
        shot = sct.grab({"left": int(left), "top": int(top), "width": int(width), "height": int(height)})
        img = np.array(shot)[:, :, :3]
        return img


def enhance_no_resize(gray):
    # 轻度去噪 + 直方图均衡（可选），不改变尺寸
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.equalizeHist(gray)
    return gray


def match_single_digit(img_bgr, templates):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = enhance_no_resize(gray)

    best_digit, best_score = None, -1.0
    for d, tpl in templates.items():
        # 若模板比ROI大，跳过（避免负尺寸匹配）
        if tpl.shape[0] > gray.shape[0] or tpl.shape[1] > gray.shape[1]:
            continue
        res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > best_score:
            best_score, best_digit = max_val, d
    return best_digit, best_score


def match_multi_digits(img_bgr, templates, thresh=0.75):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = enhance_no_resize(gray)

    hits = []
    for d, tpl in templates.items():
        if tpl.shape[0] > gray.shape[0] or tpl.shape[1] > gray.shape[1]:
            continue
        res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(res >= thresh)
        h, w = tpl.shape[:2]
        for y, x in zip(ys, xs):
            score = float(res[y, x])
            hits.append({"digit": d, "score": score, "box": (x, y, w, h)})

    # 合并重叠（仅按x轴）
    hits.sort(key=lambda k: (k["box"][0], -k["score"]))
    merged = []
    for h1 in hits:
        x1, y1, w1, h1h = h1["box"]
        overlapped = False
        for m in merged:
            x2, y2, w2, h2h = m["box"]
            # 判断水平重叠比例
            inter = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
            union = max(w1, w2)
            if inter / union > 0.3:
                if h1["score"] > m["score"]:
                    m.update(h1)
                overlapped = True
                break
        if not overlapped:
            merged.append(h1)

    merged.sort(key=lambda k: k["box"][0])
    result = "".join([m["digit"] for m in merged])
    return result, merged


def match_vertical_up_to4(img_bgr, templates, thresh=0.75, x_align_ratio=0.4, max_groups=4):
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = enhance_no_resize(gray)
    H, W = gray.shape

    # 1) 收集候选
    hits = []
    for d, tpl in templates.items():
        th, tw = tpl.shape[:2]
        if th > H or tw > W:
            continue
        res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(res >= thresh)
        for y, x in zip(ys, xs):
            score = float(res[y, x])
            hits.append({"digit": d, "score": score, "box": (x, y, tw, th)})

    if not hits:
        return "", []

    # 2) 垂直NMS：按分数从高到低剔除高度重叠的框
    hits.sort(key=lambda k: -k["score"])
    picked = []
    for h1 in hits:
        x1, y1, w1, h1h = h1["box"]
        keep = True
        for p in picked:
            x2, y2, w2, h2h = p["box"]
            inter = max(0, min(y1 + h1h, y2 + h2h) - max(y1, y2))
            union = max(h1h, h2h)
            if inter / union > 0.35:
                keep = False
                break
        if keep:
            picked.append(h1)

    # 3) x对齐过滤：竖直一列，x应接近（用w比例限定）
    xs = [p["box"][0] for p in picked]
    wavg = np.mean([p["box"][2] for p in picked]) if picked else 1
    x_mean = np.median(xs) if xs else 0
    picked = [p for p in picked if abs(p["box"][0] - x_mean) <= x_align_ratio * wavg]

    if not picked:
        return "", []

    # 4) 垂直分组：将候选按y排序并分成最多max_groups组（根据间隔）
    picked.sort(key=lambda k: k["box"][1])
    groups = []
    gap_factor = 0.5  # 邻接判断：当两个框的顶部距离超过 min(h1,h2)*gap_factor 则开新组
    for p in picked:
        x, y, w, h = p["box"]
        if not groups:
            groups.append([p])
            continue
        last = groups[-1][-1]
        _, y0, _, h0 = last["box"]
        if y - (y0 + h0) > -min(h, h0) * gap_factor:  # 允许少量重叠/紧邻
            groups[-1].append(p)
        else:
            if len(groups) < max_groups:
                groups.append([p])
            else:
                # 已满4组，跳过后续
                pass

    # 5) 每组取分数最高的一个
    chosen = []
    for g in groups[:max_groups]:
        g.sort(key=lambda k: -k["score"])
        chosen.append(g[0])

    # 6) 从上到下排序并拼接
    chosen.sort(key=lambda k: k["box"][1])
    result = "".join([c["digit"] for c in chosen])
    return result, chosen


def get_yellow_orange_mask(bgr):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lower_y = np.array([20, 120, 180], dtype=np.uint8)
    upper_y = np.array([35, 255, 255], dtype=np.uint8)
    yellow_mask = cv2.inRange(hsv, lower_y, upper_y)

    lower_o = np.array([10, 140, 90], dtype=np.uint8)
    upper_o = np.array([22, 255, 210], dtype=np.uint8)
    orange_mask = cv2.inRange(hsv, lower_o, upper_o)

    mask = cv2.bitwise_or(yellow_mask, orange_mask)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    cv2.imwrite("mask.png", mask)
    return mask
