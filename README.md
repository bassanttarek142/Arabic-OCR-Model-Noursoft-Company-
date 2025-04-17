# Arabic-OCR-Model-Noursoft-Company

This repository provides a Flask-based API for Arabic Optical Character Recognition (OCR) using ONNX model. The API is designed as a drop-in replacement for the existing Tesseract-based OCR system.

## Features

- Arabic text extraction from images using an ONNX model
- Line segmentation for improved text recognition accuracy using EasyOCR
- Compatible with existing API endpoints and database structure
- Swagger documentation for easy API testing and integration
- Support for both queue-based processing and direct image processing

## Getting Started

### Prerequisites

- Python 3.8+ 
- CUDA-compatible GPU (recommended for optimal performance)
- SQL Server database
- MongoDB for image storage (SERVER)

### Provided Files

The following essential files are included in the repository:

- `ocr_module.py` - Core OCR functionality with ONNX model integration
- `config.py` - Configuration settings for the OCR system
- `segmentor.py` - Line segmentation functionality for improved text recognition
- `exported_model/ocr_model.onnx` - The ONNX model file for Arabic text recognition
- `swagger_test_helper_onnx.py` - Helper script to generate test payloads

### Installation

1. Clone this repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Install the required dependencies:

# Install dependencies (choose one ONNX line first)
```bash
Edit requirements.txt and keep one of these lines:
 Install dependencies (choose one ONNX line first)

onnxruntime-gpu==1.19.2   # NVIDIA GPU (CUDA 11.8)
onnxruntime==1.19.2       # CPU‑only (default)
```
Then run:
```bash
pip install --upgrade pip
pip install -r requirements.txt
# optional CUDA wheel for PyTorch
# pip install torch==2.2.0+cu121 torchvision==0.17.0+cu121 \
#     --index-url https://download.pytorch.org/whl/cu121
```

3. Make sure the ONNX model is placed in the correct location:
```
./exported_model/ocr_model.onnx
```


```

### Running the API

For development:
```bash
python ocr_api_onnx.py
```

For production:
```bash
python run_ocr_api_production.py (lOCALHOST u don't need to connect to the Server)
```

The API will be available at: 
- API Service: http://10.111.10.23:5500
- Swagger Documentation: http://10.111.10.23:5500/api/docs

## API Endpoints

### Main Queue Processing Endpoint

#### `/extract_text` (POST)
Process images from the OCR queue.

**Request Body:**
```json
{
  "language": "ara",
  "psm": 3,
  "statusId": "594F800B-F7EF-486F-B56D-EFBC5DA48BD7",
  "returnedId": ""
}
```

**Response:**
```json
{
  "success": true,
  "texts": "done"
}
```

### Direct Image Processing Endpoints

#### `/api/extract_single_text` (POST)
Extract text from a single base64-encoded image.

**Request Body:**
```json
{
  "image_bytes": "base64_encoded_image_string",
  "language": "ara",
  "psm": 3
}
```

**Response:**
```json
{
  "success": true,
  "text": "extracted text with spaces",
  "lines": ["line 1", "line 2", "..."]
}
```

#### `/api/extract_multiple_text` (POST)
Extract text from multiple base64-encoded images.

**Request Body:**
```json
{
  "image_bytes_list": [
    "base64_encoded_image_1",
    "base64_encoded_image_2"
  ],
  "language": "ara",
  "psm": 3
}
```

**Response:**
```json
{
  "success": true,
  "texts": ["extracted text from image 1", "extracted text from image 2"],
  "lines_arrays": [
    ["line 1 from image 1", "line 2 from image 1"],
    ["line 1 from image 2", "line 2 from image 2"]
  ]
}
```

### Other Endpoints

#### `/get_model_info` (GET)
Get information about the OCR model.

**Response:**
```json
{
  "model_type": "ONNX OCR Model",
  "model_path": "./exported_model/ocr_model.onnx",
  "image_width": 1024,
  "image_height": 64
}
```

#### `/` (GET)
Basic endpoint to check if the API is running.

**Response:**
```json
{
  "message": "Hello"
}
```

## Testing

### Generate Test Payloads

The repository includes a helper script to generate test payloads:

```
python swagger_test_helper_onnx.py
```

This will:
1. Take sample images from the current directory
2. Convert them to base64 format
3. Create JSON payloads in the `swagger_payloads_onnx` directory with the following files:
   - `single_payload.json` - For testing single image OCR
   - `multiple_payload.json` - For testing multiple images OCR
   - `extract_text_payload.json` - For testing queue processing

### Using Swagger UI for Local Testing

1. Start the API server:
   ```
   python run_ocr_api_production.py
   ```

2. Open the Swagger UI in your browser:
   ```
   http://127.0.0.1:5500/api/docs
   ```

3. Choose the endpoint you want to test (e.g., `/api/extract_single_text`)

4. Click "Try it out" button

5. Copy the contents from the generated payload file (e.g., `swagger_payloads_onnx/single_payload.json`) and paste it into the request body field

6. Click "Execute" to see the results

This approach allows you to test the API locally without needing to connect to the server database or MongoDB instance.

## Implementation Details

### Database Integration

The system connects to:
1. SQL Server - for queue processing and result storage
2. MongoDB - for retrieving images via the API endpoint `http://localhost:7012/mongo-management/GetCollectionById`

### Text Processing

The OCR process follows these steps:
1. Image preprocessing and loading
2. Line segmentation to detect individual lines of text
3. OCR processing of each line using the ONNX model
4. Post-processing and result aggregation

### Differences from Tesseract Implementation

While maintaining API compatibility, this implementation:
- Uses an ONNX model instead of Tesseract
- Provides line-by-line text recognition for improved accuracy
- Returns both full text and separated lines in API responses
- Includes Swagger documentation for easier API testing


# 📦 Requirements

See requirements.txt – CPU build by default; switch to GPU by uncommenting one line.
© 2025 Noursoft Company — released under the MIT License.





