import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from keras.models import load_model
from keras.preprocessing import image


import requests
from io import BytesIO
import os

class DeepfakeDetector:
    def __init__(self):
        """Initialize deepfake detector"""
        self.model = None
        self.load_model()
        
        # Haar cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def load_model(self):
        """Load deepfake detection model"""
        try:
            # Try to load pre-trained model
            self.model = load_model('models/deepfake_detector.h5')
            self.img_size = (128, 128)  # Model input size
        except:
            print("Warning: Deepfake model not found. Using basic detection.")
            self.model = None
    
    def preprocess_image(self, img_array):
        """Preprocess image for model input"""
        img = Image.fromarray(img_array)
        img = img.resize(self.img_size)
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def detect_faces(self, img_array):
        """Detect faces in image"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        return faces
    
    def analyze_face(self, face_img):
        """Analyze face for deepfake indicators"""
        if self.model:
            # Use ML model
            processed = self.preprocess_image(face_img)
            prediction = self.model.predict(processed)[0][0]
            return float(prediction)
        else:
            # Basic analysis: check for inconsistencies
            # This is a simplified version - real models would be more complex
            gray = cv2.cvtColor(face_img, cv2.COLOR_RGB2GRAY)
            
            # Check for unnatural edges
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges) / (face_img.shape[0] * face_img.shape[1])
            
            # Check color consistency
            color_std = np.std(face_img, axis=(0, 1))
            color_inconsistency = np.mean(color_std)
            
            # Combine factors (simplified scoring)
            score = min(edge_density * 10 + color_inconsistency / 10, 1.0)
            return score
    
    def detect_image(self, image_path):
        """Detect deepfake in image"""
        try:
            # Load image
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # Detect faces
            faces = self.detect_faces(img_array)
            
            if len(faces) == 0:
                return {
                    'faces_detected': 0,
                    'prediction': 'No faces detected',
                    'confidence': 0,
                    'details': []
                }
            
            # Analyze each face
            results = []
            fake_scores = []
            
            for i, (x, y, w, h) in enumerate(faces):
                # Extract face
                face_img = img_array[y:y+h, x:x+w]
                
                # Analyze
                fake_score = self.analyze_face(face_img)
                fake_scores.append(fake_score)
                
                results.append({
                    'face_id': i + 1,
                    'position': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                    'fake_score': float(fake_score),
                    'is_fake': fake_score > 0.6
                })
            
            # Overall prediction
            avg_score = np.mean(fake_scores) if fake_scores else 0
            is_fake = avg_score > 0.6
            
            return {
                'faces_detected': len(faces),
                'prediction': 'Fake' if is_fake else 'Real',
                'confidence': float(abs(avg_score - 0.5) * 2),
                'fake_probability': float(avg_score),
                'real_probability': float(1 - avg_score),
                'details': results
            }
            
        except Exception as e:
            return {
                'error': f'Image analysis failed: {str(e)}',
                'prediction': 'Error'
            }
    
    def detect_video(self, video_path, sample_frames=10):
        """Detect deepfake in video"""
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if frame_count == 0:
                return {
                    'error': 'Invalid video file',
                    'prediction': 'Error'
                }
            
            # Sample frames
            sample_indices = np.linspace(0, frame_count-1, 
                                        min(sample_frames, frame_count), 
                                        dtype=int)
            
            frame_results = []
            fake_scores = []
            
            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detect faces in frame
                    faces = self.detect_faces(frame_rgb)
                    
                    if len(faces) > 0:
                        # Analyze first face found
                        x, y, w, h = faces[0]
                        face_img = frame_rgb[y:y+h, x:x+w]
                        fake_score = self.analyze_face(face_img)
                        fake_scores.append(fake_score)
                        
                        frame_results.append({
                            'frame': int(idx),
                            'faces_detected': len(faces),
                            'fake_score': float(fake_score)
                        })
            
            cap.release()
            
            if not fake_scores:
                return {
                    'frames_analyzed': len(frame_results),
                    'prediction': 'No faces detected in sampled frames',
                    'confidence': 0
                }
            
            # Overall prediction
            avg_score = np.mean(fake_scores)
            is_fake = avg_score > 0.6
            
            return {
                'frames_analyzed': len(frame_results),
                'total_frames': frame_count,
                'prediction': 'Fake' if is_fake else 'Real',
                'confidence': float(abs(avg_score - 0.5) * 2),
                'fake_probability': float(avg_score),
                'real_probability': float(1 - avg_score),
                'frame_details': frame_results
            }
            
        except Exception as e:
            return {
                'error': f'Video analysis failed: {str(e)}',
                'prediction': 'Error'
            }
    
    def detect_from_url(self, image_url):
        """Detect deepfake from image URL"""
        try:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            
            # Save temporarily
            temp_path = 'temp_image.jpg'
            img.save(temp_path)
            
            # Detect
            result = self.detect_image(temp_path)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return result
            
        except Exception as e:
            return {
                'error': f'URL analysis failed: {str(e)}',
                'prediction': 'Error'
            }