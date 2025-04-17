import base64
import json
import os
import sys
import argparse

def encode_image_to_base64(image_path):
    """Convert an image file to base64 encoded string."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def create_sample_payload(image_paths):
    """Create a sample payload for the OCR API with ONNX model."""
    encoded_images = []
    for path in image_paths:
        if not os.path.exists(path):
            print(f"Warning: File '{path}' does not exist, skipping")
            continue
            
        encoded = encode_image_to_base64(path)
        if encoded:
            encoded_images.append(encoded)
        else:
            print(f"Failed to encode image: {path}")
    
    if not encoded_images:
        print("Error: No valid images to encode")
        return None
    
    payloads = {
        "single": {
            "image_bytes": encoded_images[0],
            "language": "ara",
            "psm": 3
        },
        "multiple": {
            "image_bytes_list": encoded_images,
            "language": "ara",
            "psm": 3
        },
        "extract_text": {
            "language": "ara",
            "psm": 3,
            "statusId": "594F800B-F7EF-486F-B56D-EFBC5DA48BD7",
            "returnedId": ""
        }
    }
    
    return payloads

def save_sample_payloads(payloads, output_dir="swagger_payloads_onnx"):
    """Save the sample payloads to files."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    result = True
    for endpoint, payload in payloads.items():
        try:
            output_path = os.path.join(output_dir, f"{endpoint}_payload.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"Saved {endpoint} payload to {output_path}")
        except Exception as e:
            print(f"Error saving {endpoint} payload: {e}")
            result = False
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Create sample JSON payloads for ONNX OCR API testing')
    parser.add_argument('--images', '-i', type=str, nargs='+', 
                        help='Paths to one or more image files (Arabic text preferred)')
    parser.add_argument('--output-dir', '-o', type=str, default="swagger_payloads_onnx",
                        help='Output directory for JSON payloads (default: swagger_payloads_onnx)')
    
    args = parser.parse_args()
    
    image_paths = args.images
    if not image_paths:
        default_images = [
            "Attachment (44).JPEG",
            "Attachment (43).JPEG",
            "Attachment (24).JPEG",
            "test6.png",
        ]
        
        image_paths = []
        for img in default_images:
            if os.path.exists(img):
                image_paths.append(img)
                if len(image_paths) >= 5: 
                    break
        
        if not image_paths:
            print("Error: No default images found in the current directory. Please specify image paths.")
            sys.exit(1)
        
        print(f"Using default images: {', '.join(image_paths)}")
    
    payloads = create_sample_payload(image_paths)
    if not payloads:
        sys.exit(1)
    
    if save_sample_payloads(payloads, args.output_dir):
        print("\nTo use these payloads in Swagger UI:")
        print(f"1. Start the OCR API server: python run_ocr_api_production.py")
        print(f"2. Open the Swagger UI at http://127.0.0.1:5500/api/docs")
        print("3. Choose an endpoint to test")
        print("4. Click 'Try it out'")
        print("5. Copy the contents of the appropriate payload file into the request body field")
        print("6. Click 'Execute'")
        print("\nNOTE: This API uses an ONNX model specialized for Arabic text recognition")
        print("The 'language' and 'psm' parameters are included for API compatibility but are ignored")
    else:
        print(f"Failed to save some payloads")
        sys.exit(1)

if __name__ == "__main__":
    main() 