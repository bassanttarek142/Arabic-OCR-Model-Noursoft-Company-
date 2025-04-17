"""
ocr_module.py
-------------
Wrapper around an ONNX sequence‑to‑sequence model for Arabic OCR.
Automatically chooses GPU (CUDAExecutionProvider) if it exists,
otherwise falls back to CPUExecutionProvider.
"""
import onnxruntime as ort
import numpy as np
import cv2
from PIL import Image
from config import OCRConfig


class ONNXOCRModule:
    def __init__(self, onnx_path: str):
        # Pick the best provider automatically
        available = ort.get_available_providers()
        if "CUDAExecutionProvider" in available:
            providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
            print("✅ CUDAExecutionProvider detected – inference will run on GPU.")
        else:
            providers = ["CPUExecutionProvider"]
            print("⚠️  CUDAExecutionProvider not found – inference will run on CPU.")

        self.session = ort.InferenceSession(onnx_path, providers=providers)
        self.config = OCRConfig()

        self.PAD = self.config.PADDING_TOKEN
        self.SOS = self.config.SOS_TOKEN
        self.EOS = self.config.EOS_TOKEN
        self.NUM_TO_CHAR = self.config.num_to_char
        self.IMAGE_WIDTH = self.config.IMAGE_WIDTH
        self.IMAGE_HEIGHT = self.config.IMAGE_HEIGHT
        self.MAX_LEN = self.config.MAX_LEN

    # ------------------------------------------------------------------ helpers
    def _resize_with_padding(self, image: Image.Image, target_w: int, target_h: int) -> Image.Image:
        old_w, old_h = image.size
        ratio = min(target_w / old_w, target_h / old_h)
        new_w, new_h = int(old_w * ratio), int(old_h * ratio)
        image = image.resize((new_w, new_h), Image.BICUBIC)

        new_image = Image.new("RGB", (target_w, target_h), (255, 255, 255))
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        new_image.paste(image, (paste_x, paste_y))
        return new_image

    def _preprocess_image_array(self, image_array: np.ndarray) -> np.ndarray:
        image = Image.fromarray(image_array)
        image = self._resize_with_padding(image, self.IMAGE_WIDTH, self.IMAGE_HEIGHT)

        image = np.array(image).astype(np.float32) / 255.0
        image = np.transpose(image, (2, 0, 1))          # CHW
        image = np.expand_dims(image, axis=0)           # NCHW
        return image

    def _decode_tokens(self, token_seq: list[int]) -> str:
        result = []
        for idx in token_seq:
            if idx == self.EOS:
                break
            if idx in (self.SOS, self.PAD):
                continue
            result.append(self.NUM_TO_CHAR.get(idx, "?"))
        return "".join(result)

    # ---------------------------------------------------------------- inference
    def predict_from_array(self, image_array: np.ndarray) -> str:
        image_tensor = self._preprocess_image_array(image_array)

        tgt = np.full((1, 1), self.SOS, dtype=np.int64)
        output_text = []

        for step in range(self.MAX_LEN):
            tgt_padded = np.pad(
                tgt,
                ((0, 0), (0, self.MAX_LEN - tgt.shape[1])),
                mode="constant",
                constant_values=self.PAD,
            )

            inputs = {
                self.session.get_inputs()[0].name: image_tensor,
                self.session.get_inputs()[1].name: tgt_padded,
            }
            next_token_logits = self.session.run(None, inputs)[0][:, step, :]
            next_token = np.argmax(next_token_logits, axis=-1)

            tgt = np.concatenate([tgt, next_token[:, None]], axis=1)

            if next_token[0] == self.EOS:
                break
            output_text.append(next_token[0])

        return self._decode_tokens(output_text)

    def predict_from_path(self, image_path: str) -> str:
        img = np.array(Image.open(image_path).convert("RGB"))
        return self.predict_from_array(img)
