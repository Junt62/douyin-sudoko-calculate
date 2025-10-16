import os
import cv2
import pytesseract
import numpy as np


class ocr:
    templates = {}

    def __init__(self):
        self.templates = self.load_digit_templates()

    def load_digit_templates(self):
        templates = {}
        for d in range(1):
            p = os.path.join("templates", f"num{d+1}.png")
            img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
            if img is None:
                raise FileNotFoundError(f"模板不存在: {p}")
            templates[str(d + 1)] = img  # 不缩放
        return templates

    def find_numbers_in_region(self, image_origin, size):

        image_np = np.array(image_origin)
        if image_np.shape[2] == 4:
            image_np_convert = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
        else:
            image_np_convert = image_np

        for tmp_name, tmp_image in self.templates.items():
            result = cv2.matchTemplate(
                image_np_convert, tmp_image, cv2.TM_CCOEFF_NORMED
            )

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            threshold = 0.6
            if max_val >= threshold:
                tmp_w = tmp_image.shape[1]
                tmp_h = tmp_image.shape[0]
                top_left = max_loc
                bottom_right = (top_left[0] + tmp_w, top_left[1] + tmp_h)
                cv2.rectangle(
                    image_np_convert,
                    top_left,
                    bottom_right,
                    color=(0, 255, 0),
                    thickness=2,
                    lineType=cv2.LINE_4,
                )

                cv2.imshow("OpenCV", image_np_convert)
                cv2.waitKey()

        return

        x = size["X"]
        y = size["Y"]
        w = size["W"]
        h = size["H"]

        h, w, _ = image.shape
        x1 = int(max(0, image_size["X"]) * 2)
        y1 = int(max(0, image_size["Y"]) * 2)
        x2 = int(min(w, image_size["W"]) * 2)
        y2 = int(min(h, image_size["H"]) * 2)

        if x1 >= x2 or y1 >= y2:
            print("错误：指定区域无效或超出图片范围。")
            return []

        cropped_img = img[y1:y2, x1:x2]
        cv2.imwrite(
            os.path.join(output_dir, f"{step_name}_02_cropped.png"), cropped_img
        )
        print(f"已保存裁剪图片: {step_name}_02_cropped.png")

        # 3. 图像灰度
        gray_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(os.path.join(output_dir, f"{step_name}_03_gray.png"), gray_img)
        print(f"已保存灰度图片: {step_name}_03_gray.png")

        # 4. 二值化
        binary_img = cv2.adaptiveThreshold(
            gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        cv2.imwrite(os.path.join(output_dir, f"{step_name}_04_binary.png"), binary_img)
        print(f"已保存二值化图片: {step_name}_04_binary.png")

        found_matches = []

        templates = load_digit_templates("templates")
        for tmp_name, tmp_image in templates.items():
            # bin_tmp = cv2.adaptiveThreshold(
            #     tmp_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
            # )
            cv2.imwrite(os.path.join(output_dir, f"{step_name}_tmp_bin.png"), tmp_image)

            result = cv2.matchTemplate(gray_img, tmp_image, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= 0.7)
            h, w = tmp_image.shape[::]
            for pt in zip(
                *loc[::-1]
            ):  # zip(*loc[::-1]) 将 (array_y, array_x) 转换为 (x, y) 坐标对
                score = result[pt[1], pt[0]]  # 获取该匹配点的分数
                bottom_right = (pt[0] + w, pt[1] + h)
                found_matches.append((tmp_name, pt, bottom_right, score))
                print(f"  找到匹配: 模板 '{tmp_name}', 位置: {pt}, 分数: {score:.4f}")

        if found_matches:
            print(f"\n共找到 {len(found_matches)} 个匹配项。")
            # 绘制所有匹配项
            for template_name, top_left, bottom_right, score in found_matches:
                # 可以根据不同的模板使用不同的颜色，或者统一颜色
                color = (0, 255, 0)  # 绿色
                cv2.rectangle(gray_img, top_left, bottom_right, color, 2)
                # 可以在匹配框旁边添加文本显示模板名称和分数
                cv2.putText(
                    gray_img,
                    f"{template_name[:-4]} ({score:.2f})",
                    (top_left[0], top_left[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    1,
                )

        cv2.imshow("Source Image with All Matches", gray_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # 4. 使用Pytesseract进行OCR
        # custom_config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789"
        # text = pytesseract.image_to_string(binary_img, config=custom_config, lang="eng")

        # 5. 结果解析
        # found_numbers = [int(s) for s in text.strip().split() if s.isdigit()]

        return found_numbers
