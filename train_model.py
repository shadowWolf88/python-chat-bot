"""
train_model.py

This script provides a basic framework for training a machine learning model
on the data stored in 'training_data.db'. It focuses on loading,
preprocessing, and preparing the data for a more complex model.

This is a starting point for backend testing and is not integrated
with the live application.

To run:
1. Make sure you have scikit-learn installed:
   pip install scikit-learn pandas
2. Run the script from your terminal:
   python3 train_model.py
"""

import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

TRAINING_DB = 'training_data.db'
MODEL_OUTPUT_DIR = 'models'
VECTORIZER_PATH = os.path.join(MODEL_OUTPUT_DIR, 'tfidf_vectorizer.pkl')
MODEL_PATH = os.path.join(MODEL_OUTPUT_DIR, 'simple_model.pkl')

def load_data():
    """Loads conversation data from the training database."""
    if not os.path.exists(TRAINING_DB):
        print(f"Error: Database '{TRAINING_DB}' not found.")
        print("Please run the 'training_data_manager.py' script first to generate it.")
        return None

    print(f"Loading data from '{TRAINING_DB}'...")
    try:
        with sqlite3.connect(TRAINING_DB) as conn:
            # The 'anonymized_conversations' table seems most relevant for a chatbot
            df = pd.read_sql_query("SELECT user_input, bot_response FROM anonymized_conversations", conn)
            print(f"Loaded {len(df)} conversation pairs.")
            return df
    except Exception as e:
        print(f"Error loading data: {e}")
        print("It's possible the 'anonymized_conversations' table doesn't exist or is empty.")
        return None

def preprocess_and_train(df):
    """
    Preprocesses the text data and trains a simple model.
    For this example, we'll just create and save a TF-IDF vectorizer.
    """
    if df is None or df.empty:
        print("Skipping training due to no data.")
        return

    print("Preprocessing data and training model...")

    # Combine user and bot text to build a vocabulary
    all_text = list(df['user_input']) + list(df['bot_response'])

    # Create and train the TF-IDF vectorizer
    # This converts text into a matrix of TF-IDF features.
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    vectorizer.fit(all_text)
    print("TF-IDF vectorizer has been fitted.")

    # In a real scenario, you would use this vectorizer to transform your data
    # and feed it into a model (e.g., a classifier or a seq2seq model).
    # X = vectorizer.transform(df['user_input'])
    # y = df['bot_response']
    # model.fit(X, y)
    
    # For now, we'll just create a placeholder model object
    # This demonstrates the process of saving a "trained" model
    simple_model = {"description": "A placeholder for a real model. The real work is in the vectorizer for now."}
    print("Simple placeholder model created.")

    # Save the vectorizer and the placeholder model
    if not os.path.exists(MODEL_OUTPUT_DIR):
        os.makedirs(MODEL_OUTPUT_DIR)
        print(f"Created directory: '{MODEL_OUTPUT_DIR}'")

    with open(VECTORIZER_PATH, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"Vectorizer saved to '{VECTORIZER_PATH}'")

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(simple_model, f)
    print(f"Placeholder model saved to '{MODEL_PATH}'")


def main():
    """Main function to run the training process."""
    print("--- Starting Model Training Script ---")
    data = load_data()
    preprocess_and_train(data)
    print("--- Model Training Script Finished ---")
    print("\nNext steps:")
    print("1. Replace the placeholder model with a real one (e.g., from scikit-learn or transformers).")
    print("2. Use the saved vectorizer to transform new input before making predictions.")
    print("3. Build a prediction script that loads the model and vectorizer.")

if __name__ == '__main__':
    main()
