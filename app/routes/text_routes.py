from flask import Blueprint, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.manifold import TSNE
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import pandas as pd
import numpy as np
import os

# Create a new blueprint for text-related routes
bp = Blueprint('text', __name__)

# Download necessary NLTK resources
nltk.download('punkt')  # For sentence tokenization
nltk.download('stopwords')  # For removing common stopwords

# Route to summarize a given text
@bp.route('/summarize', methods=['POST'])
def summarize_text():
    """
    Summarize the input text by extracting the first 3 sentences.
    Input:
        - `text` (str): The text to summarize.
    Returns:
        - A JSON object with the summarized text.
    """
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Tokenize the input text into sentences
        sentences = nltk.sent_tokenize(text)
        # Use the first 3 sentences if available
        if len(sentences) > 3:
            summary = ' '.join(sentences[:3]) 
        else:
            summary = text

        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": f"Error summarizing text: {str(e)}"}), 500


# Route to extract keywords from a text
@bp.route('/keywords', methods=['POST'])
def extract_keywords():
    """
    Extract keywords from the input text using TF-IDF.
    Input:
        - `text` (str): The text for keyword extraction.
    Returns:
        - A JSON object with a list of extracted keywords.
    """
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Remove stopwords and tokenize the input text
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in stop_words and word.isalnum()]
        
        # Use TF-IDF to extract keywords
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform([' '.join(filtered_words)])
        keywords = vectorizer.get_feature_names_out()

        return jsonify({"keywords": list(keywords)}), 200
    except Exception as e:
        return jsonify({"error": f"Error extracting keywords: {str(e)}"}), 500


# Route to perform sentiment analysis on a text
@bp.route('/sentiment', methods=['POST'])
def sentiment_analysis():
    """
    Perform sentiment analysis on the input text.
    Input:
        - `text` (str): The text for sentiment analysis.
    Returns:
        - A JSON object with sentiment (Positive, Neutral, or Negative) and polarity.
    """
    text = request.json.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Use TextBlob to analyze sentiment
        analysis = TextBlob(text)
        sentiment = analysis.sentiment.polarity
        sentiment_label = "Positive" if sentiment > 0 else "Negative" if sentiment < 0 else "Neutral"

        return jsonify({"sentiment": sentiment_label, "polarity": sentiment}), 200
    except Exception as e:
        return jsonify({"error": f"Error analyzing sentiment: {str(e)}"}), 500


# Route to generate a T-SNE visualization for a list of texts
@bp.route('/tsne', methods=['POST'])
def tsne_visualization():
    """
    Generate a 2D T-SNE visualization for the input texts.
    Input:
        - `texts` (list of str): A list of texts to visualize.
    Returns:
        - A JSON object with (x, y) coordinates for each text.
    """
    texts = request.json.get("texts")
    if not texts or not isinstance(texts, list):
        return jsonify({"error": "A list of texts is required"}), 400

    try:
        # Convert texts to TF-IDF vectors
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(texts).toarray()
        
        # Adjust perplexity based on the number of texts
        perplexity = min(30, len(texts) - 1)

        # Apply T-SNE for dimensionality reduction
        tsne = TSNE(n_components=2, perplexity=perplexity, random_state=0)
        tsne_results = tsne.fit_transform(vectors)

        # Prepare the T-SNE results as a JSON response
        tsne_data = [{"x": float(x), "y": float(y), "text": text} for text, (x, y) in zip(texts, tsne_results)]
        return jsonify({"tsne": tsne_data}), 200
    except Exception as e:
        return jsonify({"error": f"Error generating T-SNE visualization: {str(e)}"}), 500


# Route to search for a query in a list of texts
@bp.route('/search', methods=['POST'])
def search_text():
    """
    Search for a query in a list of texts.
    Input:
        - `texts` (list of str): A list of texts to search in.
        - `query` (str): The search query.
    Returns:
        - A JSON object with a list of matching texts.
    """
    texts = request.json.get("texts")
    query = request.json.get("query")

    if not texts or not query:
        return jsonify({"error": "Texts and query are required"}), 400

    try:
        # Find all texts that contain the query
        results = [text for text in texts if query.lower() in text.lower()]
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": f"Error searching text: {str(e)}"}), 500
