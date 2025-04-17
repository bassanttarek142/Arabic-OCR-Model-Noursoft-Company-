import cv2
import numpy as np
import base64
import pyodbc
import uuid
import requests
import os
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from multiprocessing import Process, Queue
from flasgger import Swagger, swag_from
from PIL import Image

from ocr_module import ONNXOCRModule 
from segmentor import LineSegmenter

OCR_MODEL_PATH = "./exported_model/ocr_model.onnx"
TEMP_DIR = "./temp_files"

app = Flask(__name__)

os.makedirs(TEMP_DIR, exist_ok=True)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "info": {
        "title": "Arabic OCR API with ONNX Model",
        "description": "API for extracting Arabic text from images using an ONNX model",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header"
        }
    },
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Database connection details - use your updated credentials
# SQL Server connection details 
server = '213.6.249.126,8046'  # SQL Server's IP
database = 'Eplatform'  # Your database name
username = 'DevUser'  # Your SQL Server username
password = 'P@ssw0rd@2025##'  # Your SQL Server password

# Initialize OCR model and line segmenter
try:
    ocr_model = ONNXOCRModule(OCR_MODEL_PATH)
    line_segmenter = LineSegmenter(lang='ar')
    print("OCR model and line segmenter initialized successfully.")
except Exception as e:
    print(f"Error initializing OCR model: {e}")
    ocr_model = None
    line_segmenter = None

# Establish database connection
try:
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
    )
    cursor = conn.cursor()
    print("Connection to the SQL Server successful.")
except pyodbc.Error as e:
    print("Error connecting to SQL Server:", e)
    conn = None
    cursor = None

def guid_to_base64(guid_str):
    """Convert a GUID string to Base64 format compatible with .NET's conventions"""
    # Convert the GUID from string format to a UUID object
    guid = uuid.UUID(guid_str)
    
    # Convert to bytes and apply the .NET byte order (little-endian for the first three sections)
    little_endian_bytes = (
        guid.bytes_le[:4] +   
        guid.bytes_le[4:6] +  
        guid.bytes_le[6:8] +  
        guid.bytes[8:]        
    )
    
    # Encode to Base64 and return as a UTF-8 string
    base64_guid = base64.b64encode(little_endian_bytes).decode('utf-8')
    return base64_guid

def ocrqueu(statusId, returnedId):
    """Fetch OCR queue items from the database"""
    # If returnedId is empty, use statusId
    if not returnedId:
        returnedId = statusId
        
    query = f"""
        SELECT TOP 10 MongoDbId, EnhanceOptions, ParentId, CreatedBy, FileName, FileType, PageNo, EntryDate, CreatedDate,
        AttachmentId, Docs_DocumentId, Dynam_AttachmentId, OcrModuleId, EntryId, Code, Dynam_GroupAttachmentId
        FROM OcrQueueInfo 
        WHERE (StatusId = '{statusId}' OR StatusId = '{returnedId}') AND IsDeleted = 0
        ORDER BY EntryDate
    """

    # Execute the query
    cursor.execute(query)
    rows = cursor.fetchall()

    fileBytesList = []
    insertdataList = []

    # Process each row
    for row in rows:
        # Get MongoDB ID from the row
        mongo_id = str(row[0])
        
        # Call the external API to get the file content
        api_url = "http://localhost:7012/mongo-management/GetCollectionById"
        params = {"id": mongo_id}
        
        try:
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200 and response.content:
                data = response.json()
                
                file_content = data.get('fileBody')
                enhance_options = row[1]
                
                if enhance_options and data.get("fileEnhanceBody"):
                    file_body = data.get("fileEnhanceBody")
                else:
                    file_body = file_content
                
                if file_body:
                    fileBytesList.append(file_body)
                    
                    insertdata = {
                        "Id": str(uuid.uuid4()),
                        "MongoDbId": row[0],
                        "ParentId": row[2],
                        "CreatedBy": row[3],
                        "FileName": row[4],
                        "FileType": row[5],
                        "PageNo": row[6],
                        "ReceivedDate": row[7],
                        "CreatedDate": row[8],
                        "ExecutedDate": "",
                        "Result": "",
                        "StatusId": "",
                        "CompletedDate": datetime.now(),
                        "MisspelledText": "",
                        "AttachmentId": row[9],
                        "Docs_DocumentId": row[10],
                        "Dynam_AttachmentId": row[11],
                        "OcrModuleId": row[12],
                        "EntryId": row[13],
                        "EnhanceOptions": row[1],
                        "Code": row[14],
                        "CreationTime": datetime.now(),
                        "Dynam_GroupAttachmentId": row[15],
                        "IsDeleted": False
                    }
                    insertdataList.append(insertdata)
            else:
                print(f"Failed to retrieve data for ID {mongo_id}: Status code {response.status_code}")
                
        except Exception as e:
            print(f"Error retrieving data for ID {mongo_id}: {str(e)}")

    return fileBytesList, insertdataList

def readImage(image_bytes):
    """Convert base64 encoded image to OpenCV format"""
    image_data = base64.b64decode(image_bytes)
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def extract_text_from_image(image_bytes, image_id, result_queue, language='ar', psm='3'):
    """Segment image into lines and extract text using ONNX model"""
    image = readImage(image_bytes)
    
    temp_image_path = os.path.join(TEMP_DIR, f"temp_image_{image_id}.png")
    cv2.imwrite(temp_image_path, image)
    
    try:
        line_images = line_segmenter.segment_lines(temp_image_path, os.path.join(TEMP_DIR, f"lines_{image_id}"))
        
        if not line_images or len(line_images) == 0:
            text = ocr_model.predict_from_array(image)
            result_queue.put({'id': image_id, 'text': text if text else ""})
            return
        
        texts = []
        for idx, line_image in enumerate(line_images):
            if line_image is not None and line_image.size > 0:
                line_text = ocr_model.predict_from_array(line_image)
                if line_text:
                    line_text = line_text.strip()
                    texts.append(line_text)
        
        final_text = "\n".join(texts)
        result_queue.put({'id': image_id, 'text': final_text})
        
    except Exception as e:
        print(f"Error in extract_text_from_image: {e}")
        try:
            text = ocr_model.predict_from_array(image)
            result_queue.put({'id': image_id, 'text': text if text else ""})
        except Exception as inner_e:
            print(f"Error in fallback OCR: {inner_e}")
            result_queue.put({'id': image_id, 'text': ""})

@app.route('/extract_text', methods=['POST'])
def extract_text():
    """API endpoint to extract text from images in queue using ONNX model"""
    try:
        request_data = request.get_json()
        
        # Extract parameters (note: language and psm are kept for compatibility)
        language = request_data.get('language', 'ara')
        psm = request_data.get('psm', 3)
        statusId = request_data.get('statusId')
        returnedId = request_data.get('returnedId', '')
        
        if returnedId == "":
            returnedId = statusId
        
        # Get queued items
        image_bytes_list, insertdata = ocrqueu(statusId, returnedId)
        
        if not image_bytes_list:
            return jsonify({'success': False, 'error_message': 'No images found in queue'}), 404
        
        # Get success status ID
        cursor.execute("SELECT Id FROM OcrResultStatusLookup WHERE [Key] = 'Successed'")
        status_id_row = cursor.fetchone()
        if status_id_row:
            success_status_id = status_id_row[0]
        else:
            return jsonify({'success': False, 'error_message': 'StatusId for "Successed" not found'}), 500
        
        result_queue = Queue()
        processes = []
        
        for idx, image_bytes in enumerate(image_bytes_list, 1):
            process = Process(target=extract_text_from_image, args=(image_bytes, idx, result_queue, language, psm))
            processes.append(process)
            process.start()
        
        for process in processes:
            process.join(timeout=30)
        
        for i in range(len(insertdata)):
            if not result_queue.empty():
                queue_result = result_queue.get()
                if i < len(insertdata): 
                    text = queue_result['text'].replace('\n', ' ')
                    insertdata[i]['Result'] = text
                    insertdata[i]['MisspelledText'] = text
                    insertdata[i]['ExecutedDate'] = datetime.now()
                    insertdata[i]['StatusId'] = success_status_id
        
        insert_query = """
        INSERT INTO OcrResultInfo (
            Id, MongoDbId, ParentId, CreatedBy, FileName, FileType, PageNo, ReceivedDate, CreatedDate, 
            ExecutedDate, CreationTime, Result, StatusId, CompletedDate, MisspelledText, AttachmentId, 
            Docs_DocumentId, Dynam_AttachmentId, OcrModuleId, EntryId, EnhanceOptions, Code, 
            Dynam_GroupAttachmentId, IsDeleted
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """
        
        update_query = """
        UPDATE OcrQueueInfo 
        SET IsDeleted = 1 
        WHERE MongoDbId = ?
        """
        
        for record in insertdata:
            cursor.execute(insert_query, (
                record['Id'], record['MongoDbId'], record['ParentId'], record['CreatedBy'], record['FileName'],
                record['FileType'], record['PageNo'], record['ReceivedDate'], record['CreatedDate'],
                record['ExecutedDate'], record['CreationTime'], record['Result'], record['StatusId'], record['CompletedDate'],
                record['MisspelledText'], record['AttachmentId'], record['Docs_DocumentId'],
                record['Dynam_AttachmentId'], record['OcrModuleId'], record['EntryId'],
                record['EnhanceOptions'], record['Code'], record['Dynam_GroupAttachmentId'],
                record["IsDeleted"]
            ))
            
            cursor.execute(update_query, (record['MongoDbId'],))
        
        conn.commit()
        
        return jsonify({'success': True, 'texts': "done"})
    
    except Exception as e:
        print(f"Error in extract_text: {e}")
        return jsonify({'success': False, 'error_message': str(e)})

@app.route('/api/extract_single_text', methods=['POST'])
@swag_from({
    'tags': ['OCR'],
    'summary': 'Extract text from a single image',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'image_bytes': {
                        'type': 'string',
                        'description': 'Base64 encoded image'
                    },
                    'language': {
                        'type': 'string',
                        'description': 'Language code (parameter kept for API compatibility only, defaults to Arabic)',
                        'default': 'ara'
                    },
                    'psm': {
                        'type': 'integer',
                        'description': 'Page segmentation mode (parameter kept for API compatibility only, defaults to 3)',
                        'default': 3
                    }
                },
                'required': ['image_bytes']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {
                        'type': 'boolean'
                    },
                    'text': {
                        'type': 'string'
                    },
                    'lines': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    }
                }
            }
        }
    }
})
def extract_single_text():
    """Extract text from a single image using ONNX model"""
    try:
        request_data = request.get_json()
        
        image_bytes = request_data.get('image_bytes')
        language = request_data.get('language', 'ara')
        psm = request_data.get('psm', 3)
        
        if not image_bytes:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        result_queue = Queue()
        extract_text_from_image(image_bytes, 1, result_queue, language, psm)
        
        if not result_queue.empty():
            result = result_queue.get()
            text = result.get('text', '')
            
            lines = text.split('\n')
            full_text = ' '.join(lines)
            
            if text is not None:
                return jsonify({
                    'success': True, 
                    'text': full_text,
                    'lines': lines
                })
            else:
                return jsonify({'success': False, 'error': 'Failed to extract text'}), 500
        else:
            return jsonify({'success': False, 'error': 'No result returned'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/extract_multiple_text', methods=['POST'])
@swag_from({
    'tags': ['OCR'],
    'summary': 'Extract text from multiple images',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'image_bytes_list': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        },
                        'description': 'List of base64 encoded images'
                    },
                    'language': {
                        'type': 'string',
                        'description': 'Language code (parameter kept for API compatibility only, defaults to Arabic)',
                        'default': 'ara'
                    },
                    'psm': {
                        'type': 'integer',
                        'description': 'Page segmentation mode (parameter kept for API compatibility only, defaults to 3)',
                        'default': 3
                    }
                },
                'required': ['image_bytes_list']
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'type': 'object',
                'properties': {
                    'success': {
                        'type': 'boolean'
                    },
                    'texts': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        }
                    },
                    'lines_arrays': {
                        'type': 'array',
                        'items': {
                            'type': 'array',
                            'items': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }
    }
})
def extract_multiple_text():
    """Extract text from multiple images using ONNX model"""
    try:
        print("extract_multiple_text: Starting processing")
        request_data = request.get_json()
        
        image_bytes_list = request_data.get('image_bytes_list', [])
        language = request_data.get('language', 'ara')
        psm = request_data.get('psm', 3)
        
        print(f"extract_multiple_text: Received {len(image_bytes_list)} images")
        
        if not image_bytes_list:
            print("extract_multiple_text: No images provided")
            return jsonify({'success': False, 'error': 'No images provided'}), 400
        
        texts = []
        lines_arrays = []
        
        for idx, image_bytes in enumerate(image_bytes_list, 1):
            print(f"extract_multiple_text: Processing image {idx}")
            
            image = readImage(image_bytes)
            
            # Save the image to a temporary file for the segmenter
            temp_image_path = os.path.join(TEMP_DIR, f"temp_image_{idx}.png")
            cv2.imwrite(temp_image_path, image)
            
            try:
                line_images = line_segmenter.segment_lines(temp_image_path, os.path.join(TEMP_DIR, f"lines_{idx}"))
                
                if not line_images or len(line_images) == 0:
                    text = ocr_model.predict_from_array(image)
                    lines = [text] if text else []
                else:
                    lines = []
                    for line_image in line_images:
                        if line_image is not None and line_image.size > 0:
                            line_text = ocr_model.predict_from_array(line_image)
                            if line_text:
                                lines.append(line_text.strip())
                
                full_text = ' '.join(lines)
                
                texts.append(full_text)
                lines_arrays.append(lines)
                
                print(f"extract_multiple_text: Completed image {idx} with {len(lines)} lines")
                
            except Exception as e:
                print(f"Error processing image {idx}: {e}")
                texts.append("")
                lines_arrays.append([])
        
        print(f"extract_multiple_text: Final result has {len(texts)} texts")
        
        response = {
            'success': True, 
            'texts': texts,
            'lines_arrays': lines_arrays
        }
        
        print("extract_multiple_text: Returning response")
        return jsonify(response)
            
    except Exception as e:
        print(f"Error in extract_multiple_text: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get_model_info', methods=['GET'])
def get_model_info():
    """Get information about the OCR model"""
    return jsonify({
        'model_type': 'ONNX OCR Model',
        'model_path': OCR_MODEL_PATH,
        'image_width': ocr_model.IMAGE_WIDTH if ocr_model else 1024,
        'image_height': ocr_model.IMAGE_HEIGHT if ocr_model else 64
    })

@app.route('/', methods=['GET'])
def hello():
    """Root endpoint - returns API information"""
    return jsonify({'message': 'Hello'})

if __name__ == '__main__':
    app.run(debug=True, host='10.111.10.23', port=5500, threaded=False) 