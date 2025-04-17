"""
segmentor.py
------------
Uses EasyOCR to detect text boxes and split an image into individual lines.
Selects GPU automatically if `torch.cuda.is_available()`.
"""
import os
from typing import List

import cv2
import easyocr
import numpy as np
import torch

# Use a headless backend – no GUI windows
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class LineSegmenter:
    def __init__(self, lang: str = "ar"):
        gpu = torch.cuda.is_available()
        self.reader = easyocr.Reader([lang], gpu=gpu)
        if gpu:
            print("✅ EasyOCR initialised with GPU.")
        else:
            print("⚠️  GPU not detected – EasyOCR will run on CPU.")

    # -------------------------------------------------------------------------
    def segment_lines(self, image_path: str, output_dir: str) -> List[np.ndarray]:
        """
        Split an image into text lines.
        Returns a list of image arrays, one per line.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Detect bounding boxes
        results = self.reader.readtext(image)
        boxes = [res[0] for res in results]

        # Sort boxes top‑to‑bottom
        boxes.sort(key=lambda b: min(pt[1] for pt in b))

        # Group boxes that belong to the same line
        lines, current_line, threshold_y = [], [], 10
        for box in boxes:
            y_min = min(pt[1] for pt in box)
            if not current_line:
                current_line.append(box)
            else:
                prev_y_min = min(pt[1] for pt in current_line[-1])
                if abs(y_min - prev_y_min) < threshold_y:
                    current_line.append(box)
                else:
                    lines.append(current_line)
                    current_line = [box]
        if current_line:
            lines.append(current_line)

        os.makedirs(output_dir, exist_ok=True)
        segmented_images = []

        for idx, line_boxes in enumerate(lines):
            x_min = int(min(pt[0] for b in line_boxes for pt in b))
            x_max = int(max(pt[0] for b in line_boxes for pt in b))
            y_min = int(min(pt[1] for b in line_boxes for pt in b))
            y_max = int(max(pt[1] for b in line_boxes for pt in b))

            cropped = image[y_min:y_max, x_min:x_max]

            if cropped.size == 0:
                print(f"[WARNING] Empty segment at line {idx + 1} – skipped.")
                continue

            segment_path = os.path.join(output_dir, f"line_{idx + 1}.png")
            cv2.imwrite(segment_path, cropped)
            segmented_images.append(cropped)

            # Optional debug image
            debug_path = os.path.join(output_dir, f"line_{idx + 1}_debug.png")
            plt.figure(figsize=(10, 2))
            plt.imshow(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
            plt.axis("off")
            plt.title(f"Segmented Line {idx + 1}")
            plt.savefig(debug_path)
            plt.close()

        return segmented_images
