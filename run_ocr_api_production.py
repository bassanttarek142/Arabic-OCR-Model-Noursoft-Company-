from waitress import serve
from ocr_api_onnx import app
import os

try:
    import waitress
except ImportError:
    print("Waitress not found. Installing...")
    os.system("pip install waitress")
    print("Waitress installed successfully.")

print("Starting OCR API with Waitress production server...")
print("Server available at http://127.0.0.1:5500")
print("Swagger documentation available at http://127.0.0.1:5500/api/docs")

# Run the Flask app with Waitress
serve(app, host='127.0.0.1', port=5500, threads=4) 