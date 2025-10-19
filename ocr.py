import enum
import os
import cv2
import pytesseract
import numpy as np


class Ocr:
    templates = {}

    def __init__(self):
        self.templates = self.load_digit_templates()

    def load_digit_templates(self):
        templates = {}
        for d in range(10):
            p = os.path.join("templates", f"num{d}.png")
            image = cv2.imread(p, cv2.IMREAD_UNCHANGED)
            if image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

            if image is None:
                raise FileNotFoundError(f"模板不存在: {p}")
            templates[str(d)] = image  # 不缩放
        return templates

    def image_crop(self, image, search_range):
        x, y, w, h = (
            search_range["X"],
            search_range["Y"],
            search_range["W"],
            search_range["H"],
        )
        h_img, w_img = image.shape[:2]

        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(w_img, w)
        y1 = min(h_img, h)

        if x0 >= x1 or y0 >= y1:
            raise ValueError("裁剪区域无效或超出边界")
        return image[y0:y1, x0:x1]

    def draw_match_area(self, image, show_text, match_area):
        # 定义样式
        line_color = (0, 255, 0)
        line_type = cv2.LINE_4
        font_color = (0, 255, 0)
        font_outline_color = (0, 0, 0)
        font_type = cv2.LINE_4
        font = cv2.FONT_HERSHEY_SIMPLEX

        # 画出当前命中的区域
        XY = (match_area[0], match_area[1])
        # XY = (x, y)
        WH = (match_area[2], match_area[3])
        cv2.rectangle(image, XY, WH, line_color, 2, line_type)

        # 写出当前命中的模板名字与匹配百分比
        text = f"{show_text}"
        cv2.putText(
            image,
            text,
            (XY[0], XY[1] - 12),
            font,
            1,
            font_outline_color,
            6,
            line_type,
        )
        cv2.putText(
            image,
            text,
            (XY[0], XY[1] - 12),
            font,
            1,
            font_color,
            2,
            font_type,
        )
        return image

    def match_numbers(self, image_pillow, search_area, threshold=0.8, debug=False):
        image_np = np.array(image_pillow)
        if image_np.shape[2] == 4:
            image_np_cvt = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
        else:
            image_np_cvt = image_np

        # 裁切原图到需要搜索的范围
        search_area_scaled = {key: value * 2 for key, value in search_area.items()}
        image_np_crop = self.image_crop(image_np_cvt, search_area_scaled)

        result_nums = []
        for tmp_name, tmp_image in self.templates.items():
            # 制作原图的副本
            overlay = image_np_cvt.copy()

            # 获取当前匹配的模板的尺寸
            tmp_match_w = tmp_image.shape[1]
            tmp_match_h = tmp_image.shape[0]

            # 匹配目标
            method = cv2.TM_CCOEFF_NORMED
            result = cv2.matchTemplate(image_np_crop, tmp_image, method)

            # 获取所有匹配到的位置
            ys, xs = np.where(result >= threshold)
            locations = list(zip(xs, ys))

            # 制作矩形数组
            rectangles = []
            for loc in locations:
                rect = [int(loc[0]), int(loc[1]), tmp_match_w, tmp_match_h]
                rectangles.append(rect)
                rectangles.append(rect)

            rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.1)

            # 画出所有命中区域
            if len(rectangles):
                for x, y, w, h in rectangles:
                    X = x + search_area_scaled["X"]
                    Y = y + search_area_scaled["Y"]
                    W = X + tmp_image.shape[1]
                    H = Y + tmp_image.shape[0]
                    score = float(result[y, x])
                    overlay = self.draw_match_area(
                        overlay,
                        f"{tmp_name} {score:.3f}",
                        (
                            X,
                            Y,
                            W,
                            H,
                        ),
                    )
                    result_current = {
                        "name": tmp_name,
                        "score": round(score, 3),
                        "X": X.item(),
                        "Y": Y.item(),
                        "W": (W - X).item(),
                        "H": (H - Y).item(),
                    }
                    result_nums.append(result_current)

        # 画出匹配区域并写出匹配文字
        if debug:
            text = []
            if len(result_nums) > 0:
                for val in result_nums:
                    text.append(val["name"])
                text = ",".join(str(v) for v in text)
            self.draw_match_area(
                overlay,
                f"match: {text}",
                (
                    search_area_scaled["X"],
                    search_area_scaled["Y"],
                    search_area_scaled["W"],
                    search_area_scaled["H"],
                ),
            )
            print(result_nums)
            cv2.imshow("OpenCV", overlay)
            cv2.waitKey()

        return result_nums
