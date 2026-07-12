<<<<<<< HEAD
﻿import os
=======
﻿import os
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
import re
import shutil

import cv2
<<<<<<< HEAD
import numpy as np

try:
    import pytesseract
except Exception:
    pytesseract = None

if pytesseract is not None and shutil.which("tesseract"):
    tesseract_ok = True
else:
    tesseract_ok = False

PaddleOCR = None


class CardProcessor:
    def __init__(
        self,
        debug_dir="debug",
        tf_model_path="digit_recognizer.h5",
        dataset_dir="dataset",
        use_paddle=None,
    ):
        self.debug_dir = debug_dir
        os.makedirs(debug_dir, exist_ok=True)
        self.use_paddle = (
            os.environ.get("CARD_USE_PADDLEOCR", "0") == "1"
            if use_paddle is None
            else bool(use_paddle)
        )
=======
import numpy as np

try:
    import pytesseract
except Exception:
    pytesseract = None

if pytesseract is not None and shutil.which("tesseract"):
    tesseract_ok = True
else:
    tesseract_ok = False

PaddleOCR = None


class CardProcessor:
    def __init__(
        self,
        debug_dir="debug",
        tf_model_path="digit_recognizer.h5",
        dataset_dir="dataset",
        use_paddle=None,
    ):
        self.debug_dir = debug_dir
        os.makedirs(debug_dir, exist_ok=True)
        self.use_paddle = (
            os.environ.get("CARD_USE_PADDLEOCR", "0") == "1"
            if use_paddle is None
            else bool(use_paddle)
        )
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        self.use_tf = os.environ.get("CARD_USE_TF", "0") == "1"
        self.tf_model = self.load_tf_model(tf_model_path)
        self.digit_templates = self.load_digit_templates(dataset_dir)
        self.template_vectors = self.build_template_vectors(self.digit_templates)
        self.ocr_engine = None
        self.paddle_checked = False
        self.tesseract_cache = {}
        self.max_ocr_rois = int(os.environ.get("CARD_MAX_OCR_ROIS", "3"))
        self.max_ocr_variants = int(os.environ.get("CARD_MAX_OCR_VARIANTS", "3"))
        self.tesseract_timeout = float(os.environ.get("CARD_TESSERACT_TIMEOUT", "2.0"))
        self.ocr_call_budget = int(os.environ.get("CARD_OCR_CALL_BUDGET", "36"))
        self.ocr_calls_used = 0
<<<<<<< HEAD

    def load_tf_model(self, path):
        if not self.use_tf:
            return None
        if os.path.exists(path):
            try:
                import tensorflow as tf
            except Exception:
                print("TensorFlow unavailable, CNN fallback disabled.")
                return None
            print("TensorFlow digit model loaded.")
            return tf.keras.models.load_model(path)
        print("TensorFlow digit model not found, CNN fallback disabled.")
        return None

    def cv_imread(self, image_path):
        data = np.fromfile(image_path, dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)

    def load_digit_templates(self, dataset_dir):
        templates = {}
        if not os.path.isdir(dataset_dir):
            return templates

        for label in range(10):
            folder = os.path.join(dataset_dir, str(label))
            if not os.path.isdir(folder):
                continue
            templates[str(label)] = []
            for name in os.listdir(folder):
                if not name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    continue
                img = cv2.imread(os.path.join(folder, name), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                templates[str(label)].append(self.prepare_template_digit(img))
        return {label: imgs for label, imgs in templates.items() if imgs}

=======

    def load_tf_model(self, path):
        if not self.use_tf:
            return None
        if os.path.exists(path):
            try:
                import tensorflow as tf
            except Exception:
                print("TensorFlow unavailable, CNN fallback disabled.")
                return None
            print("TensorFlow digit model loaded.")
            return tf.keras.models.load_model(path)
        print("TensorFlow digit model not found, CNN fallback disabled.")
        return None

    def cv_imread(self, image_path):
        data = np.fromfile(image_path, dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)

    def load_digit_templates(self, dataset_dir):
        templates = {}
        if not os.path.isdir(dataset_dir):
            return templates

        for label in range(10):
            folder = os.path.join(dataset_dir, str(label))
            if not os.path.isdir(folder):
                continue
            templates[str(label)] = []
            for name in os.listdir(folder):
                if not name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                    continue
                img = cv2.imread(os.path.join(folder, name), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                templates[str(label)].append(self.prepare_template_digit(img))
        return {label: imgs for label, imgs in templates.items() if imgs}

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
    def process(self, image_path, debug=False):
        image = self.cv_imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")

        image = self.resize_for_processing(image)
        self.ocr_calls_used = 0
        best_result = None
        primary_views, fallback_views = self.build_processing_views(image)

        has_warp_view = any(view_name == "card_warp" for view_name, _, _ in primary_views)
        for view_name, view_image, view_score in primary_views:
            original_budget = self.ocr_call_budget
            if view_name == "original" and has_warp_view:
                self.ocr_call_budget = min(original_budget, 12)
            try:
                result = self.process_single_view(view_image, view_score)
            finally:
                self.ocr_call_budget = original_budget

            result["view_name"] = view_name
            if best_result is None or result["score"] > best_result["score"]:
                best_result = result
            if result["score"] >= 58 or (view_name == "card_warp" and self.is_visible_warp_number(result["number"])):
                break
            if view_name == "original" and has_warp_view:
                self.ocr_calls_used = 0

        if best_result is None or best_result["score"] < 20:
            for view_name, view_image, view_score in fallback_views:
                result = self.process_single_view(view_image, view_score)
                result["view_name"] = view_name
                if best_result is None or result["score"] > best_result["score"]:
                    best_result = result
                if best_result["score"] >= 60:
                    break

        if best_result is None:
            best_result = self.process_single_view(image, 0)
<<<<<<< HEAD

        best_number = best_result["number"]
        best_roi = best_result["roi"]
        gray = best_result["gray"]
        enhanced = best_result["enhanced"]
        binary = best_result["binary"]
        candidates_debug = best_result["candidates_debug"]
=======

        best_number = best_result["number"]
        best_roi = best_result["roi"]
        gray = best_result["gray"]
        enhanced = best_result["enhanced"]
        binary = best_result["binary"]
        candidates_debug = best_result["candidates_debug"]
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        detected = best_result["detected"]
        display_orig = best_result["image"]

        if self.ocr_calls_used >= self.ocr_call_budget and not self.is_visible_warp_number(best_number):
            best_number = None

        if debug:
<<<<<<< HEAD
            cv2.imwrite(os.path.join(self.debug_dir, "01_gray.png"), gray)
            cv2.imwrite(os.path.join(self.debug_dir, "02_enhanced.png"), enhanced)
            cv2.imwrite(os.path.join(self.debug_dir, "03_binary.png"), binary)
            cv2.imwrite(os.path.join(self.debug_dir, "04_candidates.png"), candidates_debug)
            cv2.imwrite(os.path.join(self.debug_dir, "05_detected.png"), detected)
            if best_roi is not None:
                cv2.imwrite(os.path.join(self.debug_dir, "06_roi.png"), best_roi)

        return best_number, [display_orig, gray, binary, detected, best_roi]

    def process_single_view(self, image, view_score=0):
        gray, enhanced = self.preprocess(image)
        binary, candidates_debug = self.find_number_candidates(enhanced, image)
        candidates = self.build_roi_candidates(gray, binary)

        best_number = None
        best_roi = None
        best_box = None
        best_score = -1

=======
            cv2.imwrite(os.path.join(self.debug_dir, "01_gray.png"), gray)
            cv2.imwrite(os.path.join(self.debug_dir, "02_enhanced.png"), enhanced)
            cv2.imwrite(os.path.join(self.debug_dir, "03_binary.png"), binary)
            cv2.imwrite(os.path.join(self.debug_dir, "04_candidates.png"), candidates_debug)
            cv2.imwrite(os.path.join(self.debug_dir, "05_detected.png"), detected)
            if best_roi is not None:
                cv2.imwrite(os.path.join(self.debug_dir, "06_roi.png"), best_roi)

        return best_number, [display_orig, gray, binary, detected, best_roi]

    def process_single_view(self, image, view_score=0):
        gray, enhanced = self.preprocess(image)
        binary, candidates_debug = self.find_number_candidates(enhanced, image)
        candidates = self.build_roi_candidates(gray, binary)

        best_number = None
        best_roi = None
        best_box = None
        best_score = -1

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        for candidate in candidates:
            box, roi, source_score = candidate[:3]
            number = self.recognize_card_number(roi)
            score = self.score_number(number) + source_score + view_score
            if score > best_score:
                best_number = number
                best_roi = roi
                best_box = box
                best_score = score
            if view_score >= 8 and self.is_visible_warp_number(number):
                break
            if best_score >= 58:
                break
<<<<<<< HEAD

        if best_roi is None:
            h, w = gray.shape[:2]
            fallback_rois = [
                gray[int(0.40 * h):int(0.68 * h), int(0.04 * w):int(0.96 * w)],
                gray[int(0.48 * h):int(0.78 * h), int(0.04 * w):int(0.96 * w)],
                gray[int(0.33 * h):int(0.76 * h), int(0.04 * w):int(0.96 * w)],
            ]
            for roi in fallback_rois:
                number = self.recognize_card_number(roi)
                score = self.score_number(number) + view_score
                if score > best_score:
                    best_number = number
                    best_roi = roi
                    best_score = score

        detected = image.copy()
        if best_box is not None:
            x, y, w_box, h_box = best_box
            cv2.rectangle(detected, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
            cv2.putText(
                detected,
                "CARD NUMBER",
                (x + 5, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        return {
            "number": best_number,
            "roi": best_roi,
            "box": best_box,
            "score": best_score,
            "image": image,
            "gray": gray,
            "enhanced": enhanced,
            "binary": binary,
            "candidates_debug": candidates_debug,
            "detected": detected,
        }

=======

        if best_roi is None:
            h, w = gray.shape[:2]
            fallback_rois = [
                gray[int(0.40 * h):int(0.68 * h), int(0.04 * w):int(0.96 * w)],
                gray[int(0.48 * h):int(0.78 * h), int(0.04 * w):int(0.96 * w)],
                gray[int(0.33 * h):int(0.76 * h), int(0.04 * w):int(0.96 * w)],
            ]
            for roi in fallback_rois:
                number = self.recognize_card_number(roi)
                score = self.score_number(number) + view_score
                if score > best_score:
                    best_number = number
                    best_roi = roi
                    best_score = score

        detected = image.copy()
        if best_box is not None:
            x, y, w_box, h_box = best_box
            cv2.rectangle(detected, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
            cv2.putText(
                detected,
                "CARD NUMBER",
                (x + 5, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        return {
            "number": best_number,
            "roi": best_roi,
            "box": best_box,
            "score": best_score,
            "image": image,
            "gray": gray,
            "enhanced": enhanced,
            "binary": binary,
            "candidates_debug": candidates_debug,
            "detected": detected,
        }

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
    def resize_for_processing(self, image, max_width=1400):
        h, w = image.shape[:2]
        if w <= max_width:
            return image
        scale = max_width / float(w)
        return cv2.resize(image, (max_width, int(h * scale)), interpolation=cv2.INTER_AREA)

    def build_processing_views(self, image):
        primary_views = [("original", image, 0)]
        fallback_views = []

        card_view = self.extract_card_perspective(image)
        if card_view is not None:
            primary_views.append(("card_warp", card_view, 8))

        # 小角度旋转专门处理手持拍摄时的歪斜；放在透视校正之后，避免大量慢速 OCR。
        for angle in (-6, -3, 3, 6):
            rotated = self.rotate_bound(image, angle)
            fallback_views.append((f"rotate_{angle}", rotated, -2))

        return self.unique_views(primary_views), self.unique_views(fallback_views)

    def is_visible_warp_number(self, formatted_number):
        if not formatted_number:
            return False
        digits = re.sub(r"\D", "", formatted_number)
        return len(digits) == 16 and digits.startswith("62")

    def extract_card_perspective(self, image):
        quad = self.find_card_quad(image)
        if quad is None:
            return None

        ordered = self.order_points(quad.astype("float32"))
        width_a = np.linalg.norm(ordered[2] - ordered[3])
        width_b = np.linalg.norm(ordered[1] - ordered[0])
        height_a = np.linalg.norm(ordered[1] - ordered[2])
        height_b = np.linalg.norm(ordered[0] - ordered[3])

        width = int(max(width_a, width_b))
        height = int(max(height_a, height_b))
        if width <= 0 or height <= 0:
            return None

        ratio = width / float(height)
        if ratio < 1.0:
            width, height = height, width
            ordered = np.roll(ordered, 1, axis=0)
            ratio = width / float(height)

        # 银行卡标准宽高比约 1.586；按检测比例保留一定弹性。
        target_w = 900
        target_h = int(target_w / 1.586)
        if not (1.25 <= ratio <= 2.05):
            target_h = max(360, min(680, height))
            target_w = max(600, min(1100, width))

        dst = np.array(
            [[0, 0], [target_w - 1, 0], [target_w - 1, target_h - 1], [0, target_h - 1]],
            dtype="float32",
        )
        matrix = cv2.getPerspectiveTransform(ordered, dst)
        warped = cv2.warpPerspective(image, matrix, (target_w, target_h))
        return warped

    def find_card_quad(self, image):
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        candidates = []
        for lower, upper in ((40, 120), (25, 90), (60, 160)):
            edges = cv2.Canny(gray, lower, upper)
            edges = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)), iterations=1)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < h * w * 0.12:
                    continue

                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.025 * peri, True)
                if len(approx) == 4:
                    quad = approx.reshape(4, 2)
                else:
                    rect = cv2.minAreaRect(contour)
                    quad = cv2.boxPoints(rect)

                score = self.score_card_quad(quad, area, w, h)
                if score is not None:
                    candidates.append((score, quad))

        if not candidates:
            return None
        return max(candidates, key=lambda item: item[0])[1]

    def score_card_quad(self, quad, contour_area, image_w, image_h):
        ordered = self.order_points(quad.astype("float32"))
        width = max(np.linalg.norm(ordered[2] - ordered[3]), np.linalg.norm(ordered[1] - ordered[0]))
        height = max(np.linalg.norm(ordered[1] - ordered[2]), np.linalg.norm(ordered[0] - ordered[3]))
        if width <= 0 or height <= 0:
            return None
        if width < height:
            width, height = height, width

        ratio = width / float(height)
        if not (1.15 <= ratio <= 2.15):
            return None

        rect_area = width * height
        fill = contour_area / max(1.0, rect_area)
        if fill < 0.35:
            return None

        area_ratio = rect_area / float(image_w * image_h)
        if not (0.15 <= area_ratio <= 0.98):
            return None

        ratio_score = 1.0 - min(1.0, abs(ratio - 1.586) / 0.7)
        return area_ratio * 50 + fill * 25 + ratio_score * 25

    def order_points(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def rotate_bound(self, image, angle):
        h, w = image.shape[:2]
        center = (w / 2.0, h / 2.0)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = abs(matrix[0, 0])
        sin = abs(matrix[0, 1])
        new_w = int((h * sin) + (w * cos))
        new_h = int((h * cos) + (w * sin))
        matrix[0, 2] += (new_w / 2.0) - center[0]
        matrix[1, 2] += (new_h / 2.0) - center[1]
        return cv2.warpAffine(
            image,
            matrix,
            (new_w, new_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

    def unique_views(self, views):
        unique = []
        seen = set()
        for name, view, score in views:
            key = (name, view.shape[1] // 20, view.shape[0] // 20)
            if key in seen:
                continue
            seen.add(key)
            unique.append((name, view, score))
        return unique
<<<<<<< HEAD

    def preprocess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 7, 45, 45)
        clahe = cv2.createCLAHE(clipLimit=2.8, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        blur = cv2.GaussianBlur(gray, (0, 0), 1.0)
        sharpened = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)

        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        tophat = cv2.morphologyEx(sharpened, cv2.MORPH_TOPHAT, rect_kernel)
        blackhat = cv2.morphologyEx(sharpened, cv2.MORPH_BLACKHAT, rect_kernel)
        enhanced = cv2.add(sharpened, tophat)
        enhanced = cv2.subtract(enhanced, blackhat)
        return gray, enhanced

    def find_number_candidates(self, enhanced, image):
        h, w = enhanced.shape[:2]
        debug = image.copy()
        masks = []

        grad_x = cv2.Sobel(enhanced, cv2.CV_32F, 1, 0, ksize=-1)
        grad_x = np.absolute(grad_x)
        grad_x = self.scale_to_uint8(grad_x)
        grad_x = cv2.GaussianBlur(grad_x, (5, 5), 0)
        masks.append(self.threshold_and_close(grad_x, close_kernel=(29, 5), dilate_kernel=(5, 3)))

        blackhat_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 7))
        blackhat = cv2.morphologyEx(enhanced, cv2.MORPH_BLACKHAT, blackhat_kernel)
        masks.append(self.threshold_and_close(blackhat, close_kernel=(27, 5), dilate_kernel=(7, 3)))

        tophat = cv2.morphologyEx(enhanced, cv2.MORPH_TOPHAT, blackhat_kernel)
        masks.append(self.threshold_and_close(tophat, close_kernel=(27, 5), dilate_kernel=(7, 3)))

        band_mask = np.zeros_like(enhanced)
        band_mask[int(0.32 * h):int(0.86 * h), int(0.03 * w):int(0.97 * w)] = 255

        combined = np.zeros_like(enhanced)
        boxes = []
        for mask in masks:
            mask = cv2.bitwise_and(mask, band_mask)
            combined = cv2.bitwise_or(combined, mask)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, bw, bh = cv2.boundingRect(contour)
                candidate = self.filter_number_box(x, y, bw, bh, w, h)
                if candidate is not None:
                    boxes.append(candidate)

        boxes = self.merge_boxes(boxes, w, h)
        for x, y, bw, bh in boxes:
            cv2.rectangle(debug, (x, y), (x + bw, y + bh), (0, 0, 255), 1)

        return combined, debug

    def threshold_and_close(self, src, close_kernel=(25, 5), dilate_kernel=(5, 3)):
        _, thresh = cv2.threshold(src, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        close = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            cv2.getStructuringElement(cv2.MORPH_RECT, close_kernel),
            iterations=1,
        )
        close = cv2.erode(close, np.ones((2, 2), np.uint8), iterations=1)
        close = cv2.dilate(
            close,
            cv2.getStructuringElement(cv2.MORPH_RECT, dilate_kernel),
            iterations=1,
        )
        return close

    def filter_number_box(self, x, y, bw, bh, image_w, image_h):
        ratio = bw / float(max(1, bh))
        area = bw * bh
        if not (3.0 <= ratio <= 38.0):
            return None
        if not (0.025 * image_h <= bh <= 0.22 * image_h):
            return None
        if not (0.18 * image_w <= bw <= 0.96 * image_w):
            return None
        if area < image_w * image_h * 0.003:
            return None
        if y < 0.28 * image_h or y > 0.88 * image_h:
            return None
        return (x, y, bw, bh)

    def merge_boxes(self, boxes, image_w, image_h):
        if not boxes:
            return []

        boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
        merged = []
        for box in boxes:
            x, y, w, h = box
            placed = False
            for i, prev in enumerate(merged):
                px, py, pw, ph = prev
                same_row = abs((y + h / 2) - (py + ph / 2)) < max(h, ph) * 0.85
                close_x = x <= px + pw + image_w * 0.08 and px <= x + w + image_w * 0.08
                if same_row and close_x:
                    nx = min(x, px)
                    ny = min(y, py)
                    nr = max(x + w, px + pw)
                    nb = max(y + h, py + ph)
                    merged[i] = (nx, ny, nr - nx, nb - ny)
                    placed = True
                    break
            if not placed:
                merged.append(box)

        return [b for b in merged if self.filter_number_box(*b, image_w, image_h) is not None]

    def build_roi_candidates(self, gray, binary):
        h, w = gray.shape[:2]
        candidates = []
        seen = set()

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for contour in contours:
            box = self.filter_number_box(*cv2.boundingRect(contour), w, h)
            if box is not None:
                boxes.append(box)
        boxes = self.merge_boxes(boxes, w, h)

=======

    def preprocess(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 7, 45, 45)
        clahe = cv2.createCLAHE(clipLimit=2.8, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        blur = cv2.GaussianBlur(gray, (0, 0), 1.0)
        sharpened = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)

        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 5))
        tophat = cv2.morphologyEx(sharpened, cv2.MORPH_TOPHAT, rect_kernel)
        blackhat = cv2.morphologyEx(sharpened, cv2.MORPH_BLACKHAT, rect_kernel)
        enhanced = cv2.add(sharpened, tophat)
        enhanced = cv2.subtract(enhanced, blackhat)
        return gray, enhanced

    def find_number_candidates(self, enhanced, image):
        h, w = enhanced.shape[:2]
        debug = image.copy()
        masks = []

        grad_x = cv2.Sobel(enhanced, cv2.CV_32F, 1, 0, ksize=-1)
        grad_x = np.absolute(grad_x)
        grad_x = self.scale_to_uint8(grad_x)
        grad_x = cv2.GaussianBlur(grad_x, (5, 5), 0)
        masks.append(self.threshold_and_close(grad_x, close_kernel=(29, 5), dilate_kernel=(5, 3)))

        blackhat_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 7))
        blackhat = cv2.morphologyEx(enhanced, cv2.MORPH_BLACKHAT, blackhat_kernel)
        masks.append(self.threshold_and_close(blackhat, close_kernel=(27, 5), dilate_kernel=(7, 3)))

        tophat = cv2.morphologyEx(enhanced, cv2.MORPH_TOPHAT, blackhat_kernel)
        masks.append(self.threshold_and_close(tophat, close_kernel=(27, 5), dilate_kernel=(7, 3)))

        band_mask = np.zeros_like(enhanced)
        band_mask[int(0.32 * h):int(0.86 * h), int(0.03 * w):int(0.97 * w)] = 255

        combined = np.zeros_like(enhanced)
        boxes = []
        for mask in masks:
            mask = cv2.bitwise_and(mask, band_mask)
            combined = cv2.bitwise_or(combined, mask)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                x, y, bw, bh = cv2.boundingRect(contour)
                candidate = self.filter_number_box(x, y, bw, bh, w, h)
                if candidate is not None:
                    boxes.append(candidate)

        boxes = self.merge_boxes(boxes, w, h)
        for x, y, bw, bh in boxes:
            cv2.rectangle(debug, (x, y), (x + bw, y + bh), (0, 0, 255), 1)

        return combined, debug

    def threshold_and_close(self, src, close_kernel=(25, 5), dilate_kernel=(5, 3)):
        _, thresh = cv2.threshold(src, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        close = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            cv2.getStructuringElement(cv2.MORPH_RECT, close_kernel),
            iterations=1,
        )
        close = cv2.erode(close, np.ones((2, 2), np.uint8), iterations=1)
        close = cv2.dilate(
            close,
            cv2.getStructuringElement(cv2.MORPH_RECT, dilate_kernel),
            iterations=1,
        )
        return close

    def filter_number_box(self, x, y, bw, bh, image_w, image_h):
        ratio = bw / float(max(1, bh))
        area = bw * bh
        if not (3.0 <= ratio <= 38.0):
            return None
        if not (0.025 * image_h <= bh <= 0.22 * image_h):
            return None
        if not (0.18 * image_w <= bw <= 0.96 * image_w):
            return None
        if area < image_w * image_h * 0.003:
            return None
        if y < 0.28 * image_h or y > 0.88 * image_h:
            return None
        return (x, y, bw, bh)

    def merge_boxes(self, boxes, image_w, image_h):
        if not boxes:
            return []

        boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
        merged = []
        for box in boxes:
            x, y, w, h = box
            placed = False
            for i, prev in enumerate(merged):
                px, py, pw, ph = prev
                same_row = abs((y + h / 2) - (py + ph / 2)) < max(h, ph) * 0.85
                close_x = x <= px + pw + image_w * 0.08 and px <= x + w + image_w * 0.08
                if same_row and close_x:
                    nx = min(x, px)
                    ny = min(y, py)
                    nr = max(x + w, px + pw)
                    nb = max(y + h, py + ph)
                    merged[i] = (nx, ny, nr - nx, nb - ny)
                    placed = True
                    break
            if not placed:
                merged.append(box)

        return [b for b in merged if self.filter_number_box(*b, image_w, image_h) is not None]

    def build_roi_candidates(self, gray, binary):
        h, w = gray.shape[:2]
        candidates = []
        seen = set()

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for contour in contours:
            box = self.filter_number_box(*cv2.boundingRect(contour), w, h)
            if box is not None:
                boxes.append(box)
        boxes = self.merge_boxes(boxes, w, h)

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        fallback_boxes = [
            (int(0.06 * w), int(0.52 * h), int(0.88 * w), int(0.20 * h)),
            (int(0.06 * w), int(0.58 * h), int(0.88 * w), int(0.18 * h)),
            (int(0.06 * w), int(0.45 * h), int(0.88 * w), int(0.18 * h)),
            (int(0.08 * w), int(0.40 * h), int(0.84 * w), int(0.36 * h)),
        ]
<<<<<<< HEAD

        for source_score, box in [(6, b) for b in boxes] + [(0, b) for b in fallback_boxes]:
            x, y, bw, bh = box
            pad_x = int(max(8, bw * 0.025))
            pad_y = int(max(8, bh * 0.35))
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(w, x + bw + pad_x)
            y2 = min(h, y + bh + pad_y)
=======

        for source_score, box in [(6, b) for b in boxes] + [(0, b) for b in fallback_boxes]:
            x, y, bw, bh = box
            pad_x = int(max(8, bw * 0.025))
            pad_y = int(max(8, bh * 0.35))
            x1 = max(0, x - pad_x)
            y1 = max(0, y - pad_y)
            x2 = min(w, x + bw + pad_x)
            y2 = min(h, y + bh + pad_y)
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
            key = (x1, y1, x2, y2)
            if key in seen or x2 <= x1 or y2 <= y1:
                continue
            seen.add(key)
            roi = gray[y1:y2, x1:x2]
            quality = self.score_roi_candidate(roi, (x1, y1, x2 - x1, y2 - y1), w, h)
            candidates.append(((x1, y1, x2 - x1, y2 - y1), roi, source_score, source_score + quality))

        candidates.sort(key=lambda item: item[3], reverse=True)
        return candidates[:8]

    def score_roi_candidate(self, roi, box, image_w, image_h):
        x, y, bw, bh = box
        roi_h, roi_w = roi.shape[:2]
        if roi_h <= 0 or roi_w <= 0:
            return -100.0

        full_center_y = (y + bh / 2.0) / max(1, image_h)
        full_center_x = (x + bw / 2.0) / max(1, image_w)
        height_ratio = bh / max(1, image_h)
        aspect = bw / float(max(1, bh))

        score = 0.0
        score += 22.0 - abs(full_center_y - 0.62) * 75.0
        score += 8.0 - abs(full_center_x - 0.50) * 20.0
        score += 10.0 - abs(height_ratio - 0.22) * 45.0
        score += min(12.0, aspect * 1.5)
        score += self.estimate_digit_row_score(roi)
        return score

    def estimate_digit_row_score(self, roi):
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        h_img, w_img = gray.shape[:2]
        if h_img < 20 or w_img < 80:
            return -40.0

        best = -40.0
        for binary in self.make_digit_binary_variants(gray):
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            boxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h < max(7, h_img * 0.05) or h > h_img * 0.48:
                    continue
                if w < 2 or w > w_img * 0.18:
                    continue
                if cv2.contourArea(contour) < 8:
                    continue
                boxes.append((x, y, w, h))

            for row in self.group_rows(boxes):
                if len(row) < 5:
                    continue
                x1 = min(b[0] for b in row)
                y1 = min(b[1] for b in row)
                x2 = max(b[0] + b[2] for b in row)
                y2 = max(b[1] + b[3] for b in row)
                row_w = x2 - x1
                row_h = y2 - y1
                row_center = ((y1 + y2) / 2.0) / max(1, h_img)
                row_width_ratio = row_w / max(1, w_img)
                digit_count = len(row)

                count_score = 22.0 - abs(min(digit_count, 26) - 19) * 2.2
                width_score = min(20.0, row_width_ratio * 26.0)
                center_score = 16.0 - abs(row_center - 0.66) * 45.0
                compact_score = 8.0 if row_h <= h_img * 0.42 else -8.0
                over_count_penalty = max(0, digit_count - 23) * 2.5
                top_penalty = 20.0 if row_center < 0.28 else 0.0
                bottom_penalty = 10.0 if row_center > 0.88 else 0.0
                best = max(
                    best,
                    count_score
                    + width_score
                    + center_score
                    + compact_score
                    - over_count_penalty
                    - top_penalty
                    - bottom_penalty,
                )
        return best
<<<<<<< HEAD

    def recognize_card_number(self, roi):
        if roi is None or roi.size == 0:
            return None

=======

    def recognize_card_number(self, roi):
        if roi is None or roi.size == 0:
            return None

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        rois = self.refine_number_rois(roi)[:self.max_ocr_rois]
        raw_candidates = []

        if self.get_paddle_engine() is not None:
            for roi_candidate in rois:
                for variant in self.make_ocr_variants(roi_candidate)[:self.max_ocr_variants]:
                    raw_candidates.extend(self.recognize_with_paddle(variant))

        if tesseract_ok:
            for roi_candidate in rois:
                for variant in self.make_ocr_variants(roi_candidate)[:self.max_ocr_variants]:
                    raw_candidates.extend(self.recognize_with_tesseract(variant))
                partial_number = self.pick_best_number(raw_candidates)
                partial_digits = re.sub(r"\D", "", partial_number or "")
                if len(partial_digits) >= 18 and self.score_number(partial_number) >= 45:
                    break
<<<<<<< HEAD

        if self.tf_model is not None and not raw_candidates:
            for roi_candidate in rois:
                cnn_text = self.recognize_with_tensorflow(roi_candidate)
                if cnn_text:
                    raw_candidates.append(cnn_text)

        if not raw_candidates:
            for roi_candidate in rois:
                template_text = self.recognize_with_templates(roi_candidate)
                if template_text:
                    raw_candidates.append(template_text)

        return self.pick_best_number(raw_candidates)

    def get_paddle_engine(self):
        if self.paddle_checked:
            return self.ocr_engine
        self.paddle_checked = True

        if not self.use_paddle:
            return None

        global PaddleOCR
        if PaddleOCR is None:
            try:
                from paddleocr import PaddleOCR as PaddleOCRClass

                PaddleOCR = PaddleOCRClass
            except Exception as exc:
                print("PaddleOCR import unavailable, will use other recognizers.", exc)
                return None

        if PaddleOCR is None:
            return None

        try:
            self.ocr_engine = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang="en",
            )
            print("PaddleOCR loaded.")
        except TypeError:
            try:
                self.ocr_engine = PaddleOCR(use_angle_cls=False, lang="en")
                print("PaddleOCR loaded.")
            except Exception as exc:
                self.ocr_engine = None
                print("PaddleOCR unavailable, will use other recognizers.", exc)
        except Exception as exc:
            self.ocr_engine = None
            print("PaddleOCR unavailable, will use other recognizers.", exc)

        return self.ocr_engine

    def refine_number_roi(self, roi):
        return self.refine_number_rois(roi)[0]

    def refine_number_rois(self, roi):
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        h_img, w_img = gray.shape[:2]
        if h_img < 25 or w_img < 80:
            return [gray]

        row_candidates = []
        for binary in self.make_digit_binary_variants(gray):
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            boxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h < max(7, h_img * 0.05) or h > h_img * 0.45:
                    continue
                if w < 2 or w > w_img * 0.16:
                    continue
                if cv2.contourArea(contour) < 8:
                    continue
                boxes.append((x, y, w, h))

            for row in self.group_rows(boxes):
                if len(row) < 5:
                    continue
                x1 = min(b[0] for b in row)
                y1 = min(b[1] for b in row)
                x2 = max(b[0] + b[2] for b in row)
                y2 = max(b[1] + b[3] for b in row)
                row_w = x2 - x1
                row_h = y2 - y1
                center_y = (y1 + y2) / 2
                median_h = float(np.median([b[3] for b in row]))
                score = min(len(row), 22) * 4 + row_w * 0.10 + median_h * 3
                if center_y <= 0.58 * h_img:
                    score += 25
                elif center_y > 0.72 * h_img:
                    score -= 35
                if row_w >= 0.45 * w_img:
                    score += 20
                if row_h <= h_img * 0.40:
                    score += 8
                row_candidates.append((score, (x1, y1, x2, y2)))

=======

        if self.tf_model is not None and not raw_candidates:
            for roi_candidate in rois:
                cnn_text = self.recognize_with_tensorflow(roi_candidate)
                if cnn_text:
                    raw_candidates.append(cnn_text)

        if not raw_candidates:
            for roi_candidate in rois:
                template_text = self.recognize_with_templates(roi_candidate)
                if template_text:
                    raw_candidates.append(template_text)

        return self.pick_best_number(raw_candidates)

    def get_paddle_engine(self):
        if self.paddle_checked:
            return self.ocr_engine
        self.paddle_checked = True

        if not self.use_paddle:
            return None

        global PaddleOCR
        if PaddleOCR is None:
            try:
                from paddleocr import PaddleOCR as PaddleOCRClass

                PaddleOCR = PaddleOCRClass
            except Exception as exc:
                print("PaddleOCR import unavailable, will use other recognizers.", exc)
                return None

        if PaddleOCR is None:
            return None

        try:
            self.ocr_engine = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang="en",
            )
            print("PaddleOCR loaded.")
        except TypeError:
            try:
                self.ocr_engine = PaddleOCR(use_angle_cls=False, lang="en")
                print("PaddleOCR loaded.")
            except Exception as exc:
                self.ocr_engine = None
                print("PaddleOCR unavailable, will use other recognizers.", exc)
        except Exception as exc:
            self.ocr_engine = None
            print("PaddleOCR unavailable, will use other recognizers.", exc)

        return self.ocr_engine

    def refine_number_roi(self, roi):
        return self.refine_number_rois(roi)[0]

    def refine_number_rois(self, roi):
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        h_img, w_img = gray.shape[:2]
        if h_img < 25 or w_img < 80:
            return [gray]

        row_candidates = []
        for binary in self.make_digit_binary_variants(gray):
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            boxes = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if h < max(7, h_img * 0.05) or h > h_img * 0.45:
                    continue
                if w < 2 or w > w_img * 0.16:
                    continue
                if cv2.contourArea(contour) < 8:
                    continue
                boxes.append((x, y, w, h))

            for row in self.group_rows(boxes):
                if len(row) < 5:
                    continue
                x1 = min(b[0] for b in row)
                y1 = min(b[1] for b in row)
                x2 = max(b[0] + b[2] for b in row)
                y2 = max(b[1] + b[3] for b in row)
                row_w = x2 - x1
                row_h = y2 - y1
                center_y = (y1 + y2) / 2
                median_h = float(np.median([b[3] for b in row]))
                score = min(len(row), 22) * 4 + row_w * 0.10 + median_h * 3
                if center_y <= 0.58 * h_img:
                    score += 25
                elif center_y > 0.72 * h_img:
                    score -= 35
                if row_w >= 0.45 * w_img:
                    score += 20
                if row_h <= h_img * 0.40:
                    score += 8
                row_candidates.append((score, (x1, y1, x2, y2)))

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        if not row_candidates:
            return self.expand_roi_variants([gray])

        rois = []
        seen = set()
        for _, (x1, y1, x2, y2) in sorted(row_candidates, key=lambda item: item[0], reverse=True)[:4]:
            pad_y = max(5, int((y2 - y1) * 0.22))
            pad_x = max(8, int((x2 - x1) * 0.03))
<<<<<<< HEAD
            rx1 = max(0, x1 - pad_x)
            ry1 = max(0, y1 - pad_y)
            rx2 = min(w_img, x2 + pad_x)
            ry2 = min(h_img, y2 + pad_y)
            key = (rx1, ry1, rx2, ry2)
            if key in seen or rx2 <= rx1 or ry2 <= ry1:
=======
            rx1 = max(0, x1 - pad_x)
            ry1 = max(0, y1 - pad_y)
            rx2 = min(w_img, x2 + pad_x)
            ry2 = min(h_img, y2 + pad_y)
            key = (rx1, ry1, rx2, ry2)
            if key in seen or rx2 <= rx1 or ry2 <= ry1:
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
                continue
            seen.add(key)
            rois.append(gray[ry1:ry2, rx1:rx2])
        rois.append(gray)
        return self.expand_roi_variants(rois)

    def expand_roi_variants(self, rois):
        variants = []
        for roi in rois:
            if roi is None or roi.size == 0:
                continue
            variants.append(roi)
            deskewed = self.deskew_number_roi(roi)
            if deskewed is not None:
                variants.append(deskewed)

        unique = []
        seen = set()
        for roi in variants:
            key = (roi.shape[1] // 8, roi.shape[0] // 8, int(np.mean(roi) // 8))
            if key in seen:
                continue
            seen.add(key)
            unique.append(roi)
        return unique[:6]

    def deskew_number_roi(self, roi):
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        if gray.shape[0] < 20 or gray.shape[1] < 80:
            return None

        clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8)).apply(gray)
        _, binary = cv2.threshold(clahe, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        points = []
        h_img, w_img = gray.shape[:2]
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if h < h_img * 0.15 or w < 3:
                continue
            if h > h_img * 0.85 or w > w_img * 0.25:
                continue
            points.extend(contour.reshape(-1, 2))

        if len(points) < 20:
            return None

        rect = cv2.minAreaRect(np.array(points, dtype=np.float32))
        angle = rect[-1]
        if angle < -45:
            angle += 90
        if abs(angle) < 1.2 or abs(angle) > 18:
            return None
        return self.rotate_bound(gray, angle)
<<<<<<< HEAD

    def group_rows(self, boxes):
        rows = []
        for box in sorted(boxes, key=lambda b: (b[1], b[0])):
            x, y, w, h = box
            center_y = y + h / 2
            placed = False
            for row in rows:
                row_center = np.mean([b[1] + b[3] / 2 for b in row])
                row_height = np.median([b[3] for b in row])
                if abs(center_y - row_center) <= max(h, row_height) * 0.70:
                    row.append(box)
                    placed = True
                    break
            if not placed:
                rows.append([box])
        return rows

=======

    def group_rows(self, boxes):
        rows = []
        for box in sorted(boxes, key=lambda b: (b[1], b[0])):
            x, y, w, h = box
            center_y = y + h / 2
            placed = False
            for row in rows:
                row_center = np.mean([b[1] + b[3] / 2 for b in row])
                row_height = np.median([b[3] for b in row])
                if abs(center_y - row_center) <= max(h, row_height) * 0.70:
                    row.append(box)
                    placed = True
                    break
            if not placed:
                rows.append([box])
        return rows

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
    def make_ocr_variants(self, roi):
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.copyMakeBorder(gray, 8, 8, 12, 12, cv2.BORDER_REPLICATE)
        scale = 2 if gray.shape[1] < 900 else 1
        if scale > 1:
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
        background = cv2.GaussianBlur(clahe, (0, 0), 17)
        normalized = cv2.divide(clahe, background, scale=255)
        normalized = cv2.normalize(normalized, None, 0, 255, cv2.NORM_MINMAX).astype("uint8")

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 3))
        blackhat = cv2.morphologyEx(normalized, cv2.MORPH_BLACKHAT, horizontal_kernel)
        tophat = cv2.morphologyEx(normalized, cv2.MORPH_TOPHAT, horizontal_kernel)
        digit_enhanced = cv2.add(normalized, blackhat)
        digit_enhanced = cv2.subtract(digit_enhanced, tophat // 2)

        blur = cv2.GaussianBlur(digit_enhanced, (3, 3), 0)
        _, otsu_inv = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        _, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        adaptive_inv = cv2.adaptiveThreshold(
            blur,
            255,
<<<<<<< HEAD
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            9,
        )
        adaptive = cv2.bitwise_not(adaptive_inv)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
=======
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            9,
        )
        adaptive = cv2.bitwise_not(adaptive_inv)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        otsu_inv = cv2.morphologyEx(otsu_inv, cv2.MORPH_OPEN, kernel, iterations=1)
        adaptive_inv = cv2.morphologyEx(adaptive_inv, cv2.MORPH_OPEN, kernel, iterations=1)

        return [
            gray,
            clahe,
            normalized,
            digit_enhanced,
            otsu,
            cv2.bitwise_not(otsu_inv),
            adaptive,
            cv2.bitwise_not(adaptive_inv),
        ]
<<<<<<< HEAD

    def recognize_with_paddle(self, img):
        texts = []
        try:
            result = self.ocr_engine.ocr(img, cls=False)
        except TypeError:
            result = self.ocr_engine.ocr(img)
        except Exception:
            return texts

        for item in self.flatten_paddle_result(result):
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                text_info = item[1]
                if isinstance(text_info, (list, tuple)) and text_info:
                    texts.append(str(text_info[0]))
            elif isinstance(item, dict):
                for key in ("text", "rec_text", "transcription"):
                    if key in item:
                        texts.append(str(item[key]))
        return texts

    def flatten_paddle_result(self, result):
        if result is None:
            return []
        if isinstance(result, dict):
            return [result]
        if not isinstance(result, (list, tuple)):
            return []

        if (
            len(result) >= 2
            and isinstance(result[1], (list, tuple))
            and result[1]
            and isinstance(result[1][0], str)
        ):
            return [result]

        flattened = []
        for item in result:
            if isinstance(item, dict):
                flattened.append(item)
            elif isinstance(item, (list, tuple)) and item:
                flattened.extend(self.flatten_paddle_result(item))
            else:
                flattened.append(item)
        return flattened

=======

    def recognize_with_paddle(self, img):
        texts = []
        try:
            result = self.ocr_engine.ocr(img, cls=False)
        except TypeError:
            result = self.ocr_engine.ocr(img)
        except Exception:
            return texts

        for item in self.flatten_paddle_result(result):
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                text_info = item[1]
                if isinstance(text_info, (list, tuple)) and text_info:
                    texts.append(str(text_info[0]))
            elif isinstance(item, dict):
                for key in ("text", "rec_text", "transcription"):
                    if key in item:
                        texts.append(str(item[key]))
        return texts

    def flatten_paddle_result(self, result):
        if result is None:
            return []
        if isinstance(result, dict):
            return [result]
        if not isinstance(result, (list, tuple)):
            return []

        if (
            len(result) >= 2
            and isinstance(result[1], (list, tuple))
            and result[1]
            and isinstance(result[1][0], str)
        ):
            return [result]

        flattened = []
        for item in result:
            if isinstance(item, dict):
                flattened.append(item)
            elif isinstance(item, (list, tuple)) and item:
                flattened.extend(self.flatten_paddle_result(item))
            else:
                flattened.append(item)
        return flattened

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
    def recognize_with_tesseract(self, img):
        if self.ocr_calls_used >= self.ocr_call_budget:
            return []

        cache_key = (img.shape, str(img.dtype), hash(img.tobytes()))
        if cache_key in self.tesseract_cache:
            return self.tesseract_cache[cache_key]

        texts = []
        configs = [
            "--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789",
        ]
        for config in configs:
            if self.ocr_calls_used >= self.ocr_call_budget:
                break
            self.ocr_calls_used += 1
            try:
                texts.append(pytesseract.image_to_string(img, config=config, timeout=self.tesseract_timeout))
            except Exception:
                pass
        self.tesseract_cache[cache_key] = texts
        return texts
<<<<<<< HEAD

    def recognize_with_tensorflow(self, roi):
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        variants = self.make_digit_binary_variants(gray)
        best_digits = ""

        for binary in variants:
            boxes = self.extract_digit_boxes(binary)
            if len(boxes) < len(best_digits):
                continue
            digits = []
            for x, y, w, h in boxes:
                digit_img = binary[y:y + h, x:x + w]
                digit_img = self.normalize_digit(digit_img)
                digit_img = digit_img.astype("float32") / 255.0
                digit_img = np.expand_dims(digit_img, axis=(0, -1))
                preds = self.tf_model.predict(digit_img, verbose=0)
                digits.append(str(int(np.argmax(preds))))
            candidate = "".join(digits)
            if len(candidate) > len(best_digits):
                best_digits = candidate

        return best_digits if len(best_digits) >= 10 else None

    def recognize_with_templates(self, roi):
        if not self.digit_templates:
            return None

        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        best_text = ""
        best_score = -1.0

        for binary in self.make_digit_binary_variants(gray):
            boxes = self.extract_digit_boxes(binary)
            if len(boxes) < 6:
                continue

            digits = []
            confidences = []
            for x, y, w, h in boxes[:24]:
                digit_img = binary[y:y + h, x:x + w]
                normalized = self.normalize_digit(digit_img)
                digit, confidence = self.match_digit_template(normalized)
                digits.append(digit)
                confidences.append(confidence)

            text = "".join(digits)
            if len(text) < 10:
                continue

            score = float(np.mean(confidences)) + len(text) * 0.02
            if self.luhn_check(text):
                score += 0.6
            if score > best_score:
                best_score = score
                best_text = text

        return best_text or None

    def prepare_template_digit(self, img):
        if img.size == 0:
            return np.zeros((28, 28), dtype=np.uint8)
        img = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        return binary

=======

    def recognize_with_tensorflow(self, roi):
        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        variants = self.make_digit_binary_variants(gray)
        best_digits = ""

        for binary in variants:
            boxes = self.extract_digit_boxes(binary)
            if len(boxes) < len(best_digits):
                continue
            digits = []
            for x, y, w, h in boxes:
                digit_img = binary[y:y + h, x:x + w]
                digit_img = self.normalize_digit(digit_img)
                digit_img = digit_img.astype("float32") / 255.0
                digit_img = np.expand_dims(digit_img, axis=(0, -1))
                preds = self.tf_model.predict(digit_img, verbose=0)
                digits.append(str(int(np.argmax(preds))))
            candidate = "".join(digits)
            if len(candidate) > len(best_digits):
                best_digits = candidate

        return best_digits if len(best_digits) >= 10 else None

    def recognize_with_templates(self, roi):
        if not self.digit_templates:
            return None

        gray = roi if len(roi.shape) == 2 else cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        best_text = ""
        best_score = -1.0

        for binary in self.make_digit_binary_variants(gray):
            boxes = self.extract_digit_boxes(binary)
            if len(boxes) < 6:
                continue

            digits = []
            confidences = []
            for x, y, w, h in boxes[:24]:
                digit_img = binary[y:y + h, x:x + w]
                normalized = self.normalize_digit(digit_img)
                digit, confidence = self.match_digit_template(normalized)
                digits.append(digit)
                confidences.append(confidence)

            text = "".join(digits)
            if len(text) < 10:
                continue

            score = float(np.mean(confidences)) + len(text) * 0.02
            if self.luhn_check(text):
                score += 0.6
            if score > best_score:
                best_score = score
                best_text = text

        return best_text or None

    def prepare_template_digit(self, img):
        if img.size == 0:
            return np.zeros((28, 28), dtype=np.uint8)
        img = cv2.resize(img, (28, 28), interpolation=cv2.INTER_AREA)
        _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        return binary

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
    def match_digit_template(self, digit_img):
        best_label = "0"
        best_score = -1.0
        digit_vec = digit_img.astype("float32").reshape(-1)
        digit_vec -= float(np.mean(digit_vec))
        norm = float(np.linalg.norm(digit_vec))
        if norm < 1e-6:
            return best_label, best_score
        digit_vec /= norm

        for label, vectors in self.template_vectors.items():
            if vectors.size == 0:
                continue
            scores = vectors @ digit_vec
            if scores.size == 0:
                continue
            top_count = min(5, scores.size)
            label_score = float(np.mean(np.partition(scores, -top_count)[-top_count:]))
            if label_score > best_score:
                best_label = label
                best_score = label_score

        return best_label, best_score

    def build_template_vectors(self, templates):
        vectors = {}
        for label, imgs in templates.items():
            rows = []
            for img in imgs:
                vec = img.astype("float32").reshape(-1)
                vec -= float(np.mean(vec))
                norm = float(np.linalg.norm(vec))
                if norm < 1e-6:
                    continue
                rows.append(vec / norm)
            if rows:
                vectors[label] = np.vstack(rows).astype("float32")
        return vectors
<<<<<<< HEAD

    def make_digit_binary_variants(self, gray):
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
        blur = cv2.GaussianBlur(clahe, (3, 3), 0)
        _, otsu_inv = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        adaptive_inv = cv2.adaptiveThreshold(
            blur,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            8,
        )
        return [otsu_inv, adaptive_inv]

    def extract_digit_boxes(self, binary):
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h_img, w_img = binary.shape[:2]
        boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if h < h_img * 0.16 or h > h_img * 0.95:
                continue
            if w < 3 or w > w_img * 0.18:
                continue
            if cv2.contourArea(contour) < 10:
                continue
            boxes.append((x, y, w, h))

        boxes = self.select_digit_row(self.merge_digit_fragments(sorted(boxes, key=lambda b: b[0])), h_img)
        split_boxes = []
        median_width = np.median([b[2] for b in boxes]) if boxes else 0
        for x, y, w, h in boxes:
            if median_width and w > median_width * 1.7:
                parts = max(2, int(round(w / median_width)))
                part_w = w / parts
                for i in range(parts):
                    px = int(x + i * part_w)
                    pw = int(part_w)
                    split_boxes.append((px, y, pw, h))
            else:
                split_boxes.append((x, y, w, h))
        return sorted(split_boxes, key=lambda b: b[0])

    def select_digit_row(self, boxes, image_h):
        if len(boxes) <= 6:
            return boxes

        rows = []
        for box in boxes:
            x, y, w, h = box
            center_y = y + h / 2
            placed = False
            for row in rows:
                row_center = np.mean([b[1] + b[3] / 2 for b in row])
                row_height = np.median([b[3] for b in row])
                if abs(center_y - row_center) <= max(h, row_height) * 0.65:
                    row.append(box)
                    placed = True
                    break
            if not placed:
                rows.append([box])

        def row_score(row):
            total_width = sum(b[2] for b in row)
            median_height = np.median([b[3] for b in row])
            center = np.mean([b[1] + b[3] / 2 for b in row])
            vertical_penalty = abs(center - image_h * 0.45) / max(1, image_h)
            return len(row) * 8 + total_width * 0.05 + median_height * 0.5 - vertical_penalty * 6

        best = max(rows, key=row_score)
        return sorted(best, key=lambda b: b[0])

    def merge_digit_fragments(self, boxes):
        merged = []
        for box in boxes:
            x, y, w, h = box
            if not merged:
                merged.append(box)
                continue
            px, py, pw, ph = merged[-1]
            overlap_y = min(y + h, py + ph) - max(y, py)
            close_x = x - (px + pw) <= max(2, min(w, pw) * 0.35)
            if overlap_y > min(h, ph) * 0.45 and close_x:
                nx = min(x, px)
                ny = min(y, py)
                nr = max(x + w, px + pw)
                nb = max(y + h, py + ph)
                merged[-1] = (nx, ny, nr - nx, nb - ny)
            else:
                merged.append(box)
        return merged

    def normalize_digit(self, digit_img):
        if digit_img.size == 0:
            return np.zeros((28, 28), dtype=np.uint8)
        h, w = digit_img.shape[:2]
        side = max(h, w) + 8
        canvas = np.zeros((side, side), dtype=np.uint8)
        x = (side - w) // 2
        y = (side - h) // 2
        canvas[y:y + h, x:x + w] = digit_img
        return cv2.resize(canvas, (28, 28), interpolation=cv2.INTER_AREA)

    def pick_best_number(self, raw_candidates):
        numbers = []
        raw_digit_strings = []
        for raw in raw_candidates:
            digits = re.sub(r"\D", "", str(raw))
=======

    def make_digit_binary_variants(self, gray):
        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
        blur = cv2.GaussianBlur(clahe, (3, 3), 0)
        _, otsu_inv = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        adaptive_inv = cv2.adaptiveThreshold(
            blur,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            8,
        )
        return [otsu_inv, adaptive_inv]

    def extract_digit_boxes(self, binary):
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        h_img, w_img = binary.shape[:2]
        boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if h < h_img * 0.16 or h > h_img * 0.95:
                continue
            if w < 3 or w > w_img * 0.18:
                continue
            if cv2.contourArea(contour) < 10:
                continue
            boxes.append((x, y, w, h))

        boxes = self.select_digit_row(self.merge_digit_fragments(sorted(boxes, key=lambda b: b[0])), h_img)
        split_boxes = []
        median_width = np.median([b[2] for b in boxes]) if boxes else 0
        for x, y, w, h in boxes:
            if median_width and w > median_width * 1.7:
                parts = max(2, int(round(w / median_width)))
                part_w = w / parts
                for i in range(parts):
                    px = int(x + i * part_w)
                    pw = int(part_w)
                    split_boxes.append((px, y, pw, h))
            else:
                split_boxes.append((x, y, w, h))
        return sorted(split_boxes, key=lambda b: b[0])

    def select_digit_row(self, boxes, image_h):
        if len(boxes) <= 6:
            return boxes

        rows = []
        for box in boxes:
            x, y, w, h = box
            center_y = y + h / 2
            placed = False
            for row in rows:
                row_center = np.mean([b[1] + b[3] / 2 for b in row])
                row_height = np.median([b[3] for b in row])
                if abs(center_y - row_center) <= max(h, row_height) * 0.65:
                    row.append(box)
                    placed = True
                    break
            if not placed:
                rows.append([box])

        def row_score(row):
            total_width = sum(b[2] for b in row)
            median_height = np.median([b[3] for b in row])
            center = np.mean([b[1] + b[3] / 2 for b in row])
            vertical_penalty = abs(center - image_h * 0.45) / max(1, image_h)
            return len(row) * 8 + total_width * 0.05 + median_height * 0.5 - vertical_penalty * 6

        best = max(rows, key=row_score)
        return sorted(best, key=lambda b: b[0])

    def merge_digit_fragments(self, boxes):
        merged = []
        for box in boxes:
            x, y, w, h = box
            if not merged:
                merged.append(box)
                continue
            px, py, pw, ph = merged[-1]
            overlap_y = min(y + h, py + ph) - max(y, py)
            close_x = x - (px + pw) <= max(2, min(w, pw) * 0.35)
            if overlap_y > min(h, ph) * 0.45 and close_x:
                nx = min(x, px)
                ny = min(y, py)
                nr = max(x + w, px + pw)
                nb = max(y + h, py + ph)
                merged[-1] = (nx, ny, nr - nx, nb - ny)
            else:
                merged.append(box)
        return merged

    def normalize_digit(self, digit_img):
        if digit_img.size == 0:
            return np.zeros((28, 28), dtype=np.uint8)
        h, w = digit_img.shape[:2]
        side = max(h, w) + 8
        canvas = np.zeros((side, side), dtype=np.uint8)
        x = (side - w) // 2
        y = (side - h) // 2
        canvas[y:y + h, x:x + w] = digit_img
        return cv2.resize(canvas, (28, 28), interpolation=cv2.INTER_AREA)

    def pick_best_number(self, raw_candidates):
        numbers = []
        raw_digit_strings = []
        for raw in raw_candidates:
            digits = re.sub(r"\D", "", str(raw))
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
            if not digits:
                continue
            raw_digit_strings.append(digits)
            if len(digits) == 20:
                for i in range(len(digits)):
                    corrected = digits[:i] + digits[i + 1:]
                    duplicate_bonus = 5 if (
                        (i > 0 and digits[i] == digits[i - 1])
                        or (i + 1 < len(digits) and digits[i] == digits[i + 1])
                    ) else 0
                    if i == 0 and digits[0] in "3456":
                        duplicate_bonus -= 14
                    numbers.append((corrected, duplicate_bonus))
            for size in range(19, 15, -1):
                if len(digits) == size:
                    numbers.append((digits, 0))
                elif len(digits) > size:
                    numbers.extend((digits[i:i + size], -2) for i in range(0, len(digits) - size + 1))
            repaired = self.repair_single_digit_luhn(digits)
            if repaired is not None:
                numbers.append((repaired, -4))
<<<<<<< HEAD

=======

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        valid_numbers = {}
        for number, bonus in numbers:
            if self.is_plausible_card_digits(number):
                valid_numbers[number] = max(valid_numbers.get(number, -100), bonus)
<<<<<<< HEAD

        if not valid_numbers:
            return None

        best = max(
            valid_numbers,
            key=lambda number: (
                self.score_digits(number)
                + valid_numbers[number]
                + self.context_score(number, raw_digit_strings)
            ),
        )
=======

        if not valid_numbers:
            return None

        best = max(
            valid_numbers,
            key=lambda number: (
                self.score_digits(number)
                + valid_numbers[number]
                + self.context_score(number, raw_digit_strings)
            ),
        )
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        return self.format_digits(best)

    def repair_single_digit_luhn(self, digits):
        if len(digits) != 19:
            return None
        if self.luhn_check(digits):
            return None
        if not digits.startswith(("4", "5", "6")):
            return None

        candidates = []
        for i, old_digit in enumerate(digits):
            if i < 2:
                continue
            for new_digit in "0123456789":
                if new_digit == old_digit:
                    continue
                repaired = digits[:i] + new_digit + digits[i + 1:]
                if self.luhn_check(repaired):
                    candidates.append((self.single_digit_repair_score(digits, repaired, i), repaired))

        if not candidates:
            return None
        candidates.sort(reverse=True)
        if candidates[0][0] < 65:
            return None
        return candidates[0][1]

    def single_digit_repair_score(self, original, repaired, index):
        score = self.score_digits(repaired)
        original_digit = original[index]
        repaired_digit = repaired[index]
        if index < 8:
            score -= 14
        elif index < 12:
            score -= 8
        elif index < 14:
            score -= 4
        if index >= len(original) - 3:
            score -= 12
        elif index >= len(original) - 4:
            score -= 6
        known_confusion = False
        if (original_digit, repaired_digit) in {
            ("9", "3"),
            ("3", "9"),
        }:
            score += 3
            known_confusion = True
        if (original_digit, repaired_digit) in {
            ("5", "3"),
            ("3", "5"),
        }:
            score += 7
            known_confusion = True
        if (original_digit, repaired_digit) in {
            ("5", "6"),
            ("6", "5"),
            ("1", "7"),
            ("7", "1"),
        }:
            score += 4
            known_confusion = True
        if (original_digit, repaired_digit) in {
            ("8", "0"),
            ("0", "8"),
        }:
            score += 1
            known_confusion = True
        if not known_confusion:
            score -= 8
        return score
<<<<<<< HEAD

    def context_score(self, number, raw_digit_strings):
        score = 0
        for size, weight in ((16, 5), (12, 3), (10, 1)):
            if len(number) < size:
                continue
            prefix = number[:size]
            hits = sum(1 for raw in raw_digit_strings if prefix in raw)
            score += min(15, hits * weight)
        for size, weight in ((4, 3), (3, 2)):
            if len(number) < size:
                continue
            suffix = number[-size:]
            hits = sum(1 for raw in raw_digit_strings if suffix in raw)
            score += min(10, hits * weight)
=======

    def context_score(self, number, raw_digit_strings):
        score = 0
        for size, weight in ((16, 5), (12, 3), (10, 1)):
            if len(number) < size:
                continue
            prefix = number[:size]
            hits = sum(1 for raw in raw_digit_strings if prefix in raw)
            score += min(15, hits * weight)
        for size, weight in ((4, 3), (3, 2)):
            if len(number) < size:
                continue
            suffix = number[-size:]
            hits = sum(1 for raw in raw_digit_strings if suffix in raw)
            score += min(10, hits * weight)
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
        return score

    def has_suspicious_repetition(self, number):
        if re.search(r"(\d)\1{4,}", number):
            return True
        counts = {digit: number.count(digit) for digit in set(number)}
        most_common = max(counts.values()) if counts else 0
        top_two = sum(sorted(counts.values(), reverse=True)[:2])
        if not number.startswith("62") and top_two >= 10:
            return True
        return most_common >= max(9, int(len(number) * 0.58))

    def is_plausible_card_digits(self, number):
        if not (16 <= len(number) <= 19):
            return False
        if self.has_suspicious_repetition(number):
            return False
        if number.startswith("62"):
            return True
        if number.startswith(("4", "5", "6")):
            return len(number) >= 18 and self.luhn_check(number)
        return False

    def score_number(self, formatted_number):
<<<<<<< HEAD
        if not formatted_number:
            return -100
        digits = re.sub(r"\D", "", formatted_number)
        return self.score_digits(digits)

=======
        if not formatted_number:
            return -100
        digits = re.sub(r"\D", "", formatted_number)
        return self.score_digits(digits)

>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
    def score_digits(self, number):
        score = len(number)
        if 16 <= len(number) <= 19:
            score += 8
        elif 13 <= len(number) < 16:
            score -= 8
        if len(number) >= 18:
            score += 12
        if self.luhn_check(number):
            score += 20
        if number.startswith("62"):
            score += 8
            if len(number) > 16 and not self.luhn_check(number):
                score -= 18
        elif number.startswith(("4", "5", "6")):
            score += 5
        elif number.startswith(("1", "2", "3", "7", "8", "9")):
            score -= 16
        return score
<<<<<<< HEAD

    def format_digits(self, number):
        return " ".join(number[i:i + 4] for i in range(0, len(number), 4))

    def scale_to_uint8(self, src):
        min_val, max_val = np.min(src), np.max(src)
        if max_val - min_val < 1e-6:
            return np.zeros_like(src, dtype=np.uint8)
        return ((src - min_val) * 255.0 / (max_val - min_val)).astype("uint8")

    def luhn_check(self, number):
        if not number or not number.isdigit():
            return False
        digits = [int(d) for d in str(number)][::-1]
        total = 0
        for i, digit in enumerate(digits):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        return total % 10 == 0
=======

    def format_digits(self, number):
        return " ".join(number[i:i + 4] for i in range(0, len(number), 4))

    def scale_to_uint8(self, src):
        min_val, max_val = np.min(src), np.max(src)
        if max_val - min_val < 1e-6:
            return np.zeros_like(src, dtype=np.uint8)
        return ((src - min_val) * 255.0 / (max_val - min_val)).astype("uint8")

    def luhn_check(self, number):
        if not number or not number.isdigit():
            return False
        digits = [int(d) for d in str(number)][::-1]
        total = 0
        for i, digit in enumerate(digits):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        return total % 10 == 0
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
