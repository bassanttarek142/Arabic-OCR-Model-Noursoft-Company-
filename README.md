# Arabic-OCR-Model-Noursoft-Company-
A Flask‑based API that performs Arabic Optical Character Recognition (OCR) using an exported ONNX sequence‑to‑sequence model. It is designed as a drop‑in replacement for a legacy Tesseract solution while providing higher accuracy and a modern Swagger interface.

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **ONNX model** | CNN Transformer encoder‑decoder(Hybird approach) trained for Arabic text, shipped in `exported_model/ocr_model.onnx`. |
| **Line segmentation** | Uses EasyOCR + custom grouping logic to feed cleaner line crops into the model. |
| **CPU & GPU auto‑detection** | Runs on CUDA when available; otherwise falls back to CPU transparently. |
| **Swagger UI** | Self‑documenting endpoints at `/api/docs` for quick testing & integration. |
| **Queue & Direct modes** | Process images pulled from a SQL queue *or* send Base64 images directly. |

---

## 🗂 Repository Layout


## 🚀 Quick Start

### 1 – Clone / download
```bash
git clone <REPO_URL>
cd Arabic-OCR-Model-Noursoft-Company-

2 – Create and activate a fresh Python environment
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate


3 – Install dependencies (choose one ONNX line first)
Open requirements.txt and keep one of these two lines:
onnxruntime-gpu==1.19.2   # NVIDIA GPU (CUDA 11.8)
onnxruntime==1.19.2       # CPU‑only (default)


Then run:
pip install --upgrade pip
pip install -r requirements.txt
# optional CUDA wheel for PyTorch
# pip install torch==2.2.0+cu121 torchvision==0.17.0+cu121 --index-url https://download.pytorch.org/whl/cu121
