import numpy as np
import cv2
from deepface import DeepFace

def extract_face_embedding(image_path):
    try:
        embedding = DeepFace.represent(image_path, model_name="Facenet")[0]["embedding"]
        return np.array(embedding, dtype=np.float32).tobytes()
    except:
        return None

def compare_embeddings(embedding1, embedding2):
    emb1 = np.frombuffer(embedding1, dtype=np.float32)
    emb2 = np.frombuffer(embedding2, dtype=np.float32)
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity >= 0.95