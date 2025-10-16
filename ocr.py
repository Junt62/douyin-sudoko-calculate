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
        for d in range(10):
            p = os.path.join("templates", f"num{d}.png")
            image = cv2.imread(p, cv2.IMREAD_UNCHANGED)
            if image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

            if image is None:
                raise FileNotFoundError(f"模板不存在: {p}")
            templates[str(d)] = image  # 不缩放
        return templates

    def find_numbers_in_region(self, image_pillow, size):
        image_np = np.array(image_pillow)
        if image_np.shape[2] == 4:
            image_np_convert = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
        else:
            image_np_convert = image_np

        result_num = []
        for tmp_name, tmp_image in self.templates.items():
            result = cv2.matchTemplate(
                image_np_convert, tmp_image, cv2.TM_CCOEFF_NORMED
            )

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            threshold = 0.8
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

                label = f"{tmp_name}"
                cv2.putText(
                    image_np_convert,
                    label,
                    (top_left[0] - 24, top_left[1] + 24),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    thickness=2,
                    lineType=cv2.LINE_4,
                )

                cv2.imshow("OpenCV", image_np_convert)
                cv2.waitKey()
                result_num.append(tmp_name)

        return result_num
