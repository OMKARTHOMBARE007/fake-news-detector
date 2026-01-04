"""
Script to train fake news detection model
Note: You'll need a dataset to train this model
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import pickle

def prepare_sample_data():
    """Create sample data if no dataset is available"""
    # This is a simplified example - use real datasets for production
    
    sample_data = {
        'text': [
            'Breaking: Shocking discovery that will change everything!',
            'Scientists confirm new breakthrough in renewable energy.',
            'Government hiding the truth about alien encounters!',
            'The stock market showed steady growth today.',
            'You wont believe what this celebrity did! Must watch!',
            'Economic indicators suggest positive outlook for next quarter.',
            'Secret recipe that doctors dont want you to know about!',
            'Research shows benefits of regular exercise and healthy diet.',
            'Viral video exposes shocking conspiracy!',
            'Weather forecast predicts sunny days ahead.'
        ],
        'label': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # 1 = Fake, 0 = Real
    }
    
    return pd.DataFrame(sample_data)

def train_fake_news_model():
    """Train fake news detection model"""
    print("Training fake news detection model...")
    
    # Load your dataset here
    # df = pd.read_csv('your_dataset.csv')
    
    # For demo, create sample data
    df = prepare_sample_data()
    
    # Prepare data
    X = df['text']
    y = df['label']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Create TF-IDF features
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Train model
    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train_tfidf, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Model Accuracy: {accuracy:.2f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model and vectorizer
    joblib.dump(model, 'models/fake_news_detector.pkl')
    joblib.dump(vectorizer, 'models/vectorizer.pkl')
    
    print("\nModel saved successfully!")
    
    return model, vectorizer

if __name__ == '__main__':
    train_fake_news_model()