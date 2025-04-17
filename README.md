# Arabic-OCR-Model-Noursoft-Company-
A Flask‑based API that performs Arabic Optical Character Recognition (OCR) using an exported ONNX sequence‑to‑sequence model. It is designed as a drop‑in replacement for a legacy Tesseract solution while providing higher accuracy and a modern Swagger interface.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **ONNX model** | Transformer encoder‑decoder trained for Arabic text, shipped in `exported_model/ocr_model.onnx`. |
| **Line segmentation** | Uses EasyOCR + custom grouping logic to feed cleaner line crops into the model. |
| **CPU & GPU auto‑detection** | Runs on CUDA when available; otherwise falls back to CPU transparently. |
| **Swagger UI** | Self‑documenting endpoints at `/api/docs` for quick testing & integration. |
| **Queue & Direct modes** | Process images pulled from a SQL queue *or* send Base64 images directly. |

---

## 🗂 Repository Layout
