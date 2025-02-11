import requests
import json
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

COMPREFACE_URL = "http://localhost:8000/api/v1"
API_KEY = os.getenv("API_KEY")

def register_face(image_data, subject):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name

        file_obj = open(temp_file_path, 'rb')

        url = f"{COMPREFACE_URL}/recognition/faces"
        files = {'file': ('image.jpg', file_obj, 'image/jpeg')}
        data = {'subject': subject, 'det_prob_threshold': 0.8}
        headers = {"x-api-key": API_KEY}

        response = requests.post(url, files=files, data=data, headers=headers)

        file_obj.close()

        os.unlink(temp_file_path)

        if response.status_code == 201:
            result = response.json()
            return result.get('image_id')

        return None

    except Exception as e:
        print(f"Error in register_face: {str(e)}")
        return None

def verify_face(image_data, subject):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name

        file_obj = open(temp_file_path, 'rb')

        url = f"{COMPREFACE_URL}/recognition/recognize"
        files = {'file': ('image.jpg', file_obj, 'image/jpeg')}
        data = {'det_prob_threshold': 0.8, 'limit': 1, 'prediction_count': 1}
        headers = {"x-api-key": API_KEY}

        response = requests.post(url, files=files, data=data, headers=headers)

        file_obj.close()
        os.unlink(temp_file_path)

        if response.status_code == 200:
            result = response.json()
            if result.get('result') and len(result['result']) > 0:
                face_result = result['result'][0]
                if face_result.get('subjects') and len(face_result['subjects']) > 0:
                    matched_subject = face_result['subjects'][0]
                    return (matched_subject['subject'] == subject and 
                            matched_subject['similarity'] >= 0.9)

        return False

    except Exception as e:
        print(f"Error in verify_face: {str(e)}")
        return False
