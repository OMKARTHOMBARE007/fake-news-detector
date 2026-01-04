import re
import pickle
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import warnings
warnings.filterwarnings('ignore')

class NewsAnalyzer:
    def __init__(self):
        """Initialize news analyzer with ML models"""
        try:
            # Load pre-trained models
            self.vectorizer = joblib.load('models/vectorizer.pkl')
            self.model = joblib.load('models/fake_news_detector.pkl')
            self.features = [
                'text_length', 'has_exclamation', 'has_question',
                'capital_ratio', 'number_count', 'url_count',
                'sentiment_score', 'subjectivity_score'
            ]
        except:
            # Fallback to simple model if trained models aren't available
            self.vectorizer = None
            self.model = None
            print("Warning: Using rule-based analyzer. Train models for better accuracy.")
    
    def extract_features(self, text):
        """Extract linguistic features from text"""
        features = {}
        
        # Text length
        features['text_length'] = len(text)
        
        # Punctuation features
        features['has_exclamation'] = int('!' in text)
        features['has_question'] = int('?' in text)
        
        # Capitalization ratio
        caps = sum(1 for c in text if c.isupper())
        features['capital_ratio'] = caps / len(text) if text else 0
        
        # Number count
        features['number_count'] = len(re.findall(r'\d+', text))
        
        # URL count
        features['url_count'] = len(re.findall(r'http[s]?://\S+', text))
        
        # Sentiment analysis (simplified)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'fake']
        
        words = text.lower().split()
        pos_count = sum(1 for word in words if word in positive_words)
        neg_count = sum(1 for word in words if word in negative_words)
        
        features['sentiment_score'] = (pos_count - neg_count) / len(words) if words else 0
        features['subjectivity_score'] = (pos_count + neg_count) / len(words) if words else 0
        
        return features
    
    def analyze_text(self, text, method='ml'):
        """Analyze text for fake news indicators"""
        
        if method == 'ml' and self.model:
            # ML-based analysis
            try:
                # Transform text
                text_tfidf = self.vectorizer.transform([text])
                
                # Predict
                prediction = self.model.predict(text_tfidf)[0]
                probability = self.model.predict_proba(text_tfidf)[0]
                
                result = {
                    'text': text[:500] + '...' if len(text) > 500 else text,
                    'prediction': 'Fake' if prediction == 1 else 'Real',
                    'confidence': float(max(probability)),
                    'fake_probability': float(probability[1]),
                    'real_probability': float(probability[0]),
                    'method': 'Machine Learning'
                }
            except:
                # Fallback to rule-based
                result = self._rule_based_analysis(text)
        else:
            # Rule-based analysis
            result = self._rule_based_analysis(text)
        
        # Add linguistic analysis
        features = self.extract_features(text)
        result['linguistic_features'] = features
        
        # Add warning flags
        warnings = self._check_warnings(text, features)
        result['warnings'] = warnings
        
        return result
    
    def _rule_based_analysis(self, text):
        """Rule-based fake news detection"""
        text_lower = text.lower()
        
        # Common fake news indicators
        fake_indicators = [
            r'breaking.*exclusive',
            r'you won.*believe',
            r'shocking.*truth',
            r'government.*cover.up',
            r'must read.*share',
            r'viral.*video',
            r'doctors hate this',
            r'they don.*want you to know'
        ]
        
        score = 0
        for indicator in fake_indicators:
            if re.search(indicator, text_lower):
                score += 1
        
        # Calculate score
        fake_score = min(score / len(fake_indicators), 1.0)
        
        return {
            'prediction': 'Fake' if fake_score > 0.6 else 'Real',
            'confidence': abs(fake_score - 0.5) * 2,
            'fake_probability': fake_score,
            'real_probability': 1 - fake_score,
            'method': 'Rule-Based'
        }
    
    def _check_warnings(self, text, features):
        """Check for specific warning signs"""
        warnings = []
        
        if features['capital_ratio'] > 0.3:
            warnings.append('Excessive capitalization detected')
        
        if features['url_count'] > 3:
            warnings.append('Multiple URLs detected')
        
        if features['has_exclamation'] and text.count('!') > 3:
            warnings.append('Excessive exclamation marks')
        
        if features['text_length'] < 50:
            warnings.append('Text is very short')
        
        if features['subjectivity_score'] > 0.3:
            warnings.append('Highly subjective language detected')
        
        return warnings
    
    def analyze_url(self, url, method='ml'):
        """Extract and analyze content from URL"""
        try:
            # Fetch URL content
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text (simplified)
            text = soup.get_text()
            
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Analyze extracted text
            result = self.analyze_text(text, method)
            result['url'] = url
            result['title'] = soup.title.string if soup.title else 'No title'
            
            return result
            
        except Exception as e:
            return {
                'error': f'Failed to analyze URL: {str(e)}',
                'url': url,
                'prediction': 'Unknown'
            }