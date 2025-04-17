# Arabic-OCR-Model-Noursoft-Company-
A Flask‑based API that performs Arabic Optical Character Recognition (OCR) using an exported ONNX sequence‑to‑sequence model. It is designed as a drop‑in replacement for a legacy Tesseract solution while providing higher accuracy and a modern Swagger interface.

✨ Key Features

Feature

Description

ONNX model

Transformer encoder‑decoder trained for Arabic text, shipped in exported_model/ocr_model.onnx.

Line segmentation

Uses EasyOCR + custom grouping logic to feed cleaner line crops into the model.

**CPU **& GPU auto‑detection

If CUDA is available the API runs on GPU; otherwise it automatically falls back to CPU.

Swagger UI

Self‑documenting endpoints at /api/docs for quick testing & integration.

Queue / Direct modes

Process documents from a SQL‑based job queue or send Base64 images directly.
