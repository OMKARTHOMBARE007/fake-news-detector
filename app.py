import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image
import cv2
import json

from utils.news_detector import NewsAnalyzer
from utils.deepfake_detector import DeepfakeDetector

# Initialize Flask app
app = Flask(__name__)
app.config.from_pyfile('config.py')

# Create upload directories if they don't exist
os.makedirs('static/uploads/text', exist_ok=True)
os.makedirs('static/uploads/images', exist_ok=True)
os.makedirs('static/uploads/videos', exist_ok=True)

# Initialize detectors
news_analyzer = NewsAnalyzer()
deepfake_detector = DeepfakeDetector()

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

@app.route('/')
def index():
    """Home page with detection options"""
    return render_template('index.html')

@app.route('/detect-news', methods=['POST'])
def detect_news():
    """Detect fake news from text input or URL"""
    try:
        data_type = request.form.get('data_type', 'text')
        detection_method = request.form.get('detection_method', 'ml')
        
        if data_type == 'text':
            text = request.form.get('text', '')
            if not text.strip():
                return jsonify({'error': 'Please enter text to analyze'}), 400
            
            # Analyze text
            result = news_analyzer.analyze_text(text, method=detection_method)
            
        elif data_type == 'url':
            url = request.form.get('url', '')
            if not url.strip():
                return jsonify({'error': 'Please enter a URL to analyze'}), 400
            
            # Analyze URL content
            result = news_analyzer.analyze_url(url, method=detection_method)
        
        else:
            return jsonify({'error': 'Invalid data type'}), 400
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in detect_news: {str(e)}")
        return jsonify({'error': 'An error occurred during analysis'}), 500

@app.route('/detect-deepfake', methods=['POST'])
def detect_deepfake():
    """Detect deepfake in images or videos"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Check file type and save accordingly
        if allowed_image_file(filename):
            filepath = os.path.join('static/uploads/images', unique_filename)
            file.save(filepath)
            
            # Detect deepfake in image
            result = deepfake_detector.detect_image(filepath)
            
        elif allowed_video_file(filename):
            filepath = os.path.join('static/uploads/videos', unique_filename)
            file.save(filepath)
            
            # Detect deepfake in video
            result = deepfake_detector.detect_video(filepath)
            
        else:
            return jsonify({'error': 'File type not supported. Use images or videos.'}), 400
        
        # Add file info to result
        result['filename'] = unique_filename
        result['file_type'] = 'image' if allowed_image_file(filename) else 'video'
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in detect_deepfake: {str(e)}")
        return jsonify({'error': 'An error occurred during analysis'}), 500

@app.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple news articles at once"""
    try:
        articles = request.json.get('articles', [])
        if not articles:
            return jsonify({'error': 'No articles provided'}), 400
        
        results = []
        for article in articles:
            if 'text' in article:
                result = news_analyzer.analyze_text(article['text'])
                results.append(result)
        
        # Calculate overall statistics
        total = len(results)
        fake_count = sum(1 for r in results if r.get('prediction') == 'Fake')
        real_count = total - fake_count
        
        summary = {
            'total_articles': total,
            'fake_articles': fake_count,
            'real_articles': real_count,
            'fake_percentage': (fake_count / total * 100) if total > 0 else 0,
            'details': results
        }
        
        return jsonify(summary)
        
    except Exception as e:
        app.logger.error(f"Error in batch_analyze: {str(e)}")
        return jsonify({'error': 'An error occurred during batch analysis'}), 500

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for programmatic access"""
    try:
        data = request.json
        
        if 'text' in data:
            result = news_analyzer.analyze_text(data['text'])
        elif 'image_url' in data:
            # Download and analyze image
            result = deepfake_detector.detect_from_url(data['image_url'])
        else:
            return jsonify({'error': 'Invalid request format'}), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    """Display analytics dashboard"""
    # This would typically load from a database
    stats = {
        'total_checks': 1500,
        'fake_detected': 320,
        'accuracy': 94.5,
        'recent_activity': []
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/results')
def results_page():
    """Display detailed results page"""
    return render_template('results.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)