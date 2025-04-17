Test payloads will be generated in this directory when you run:

python swagger_test_helper_onnx.py

or use the batch file:

generate_test_payloads.bat

The generated files will include:
- single_payload.json - For testing single image OCR
- multiple_payload.json - For testing multiple images OCR
- extract_text_payload.json - For testing queue processing 