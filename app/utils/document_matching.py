import hashlib
from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from app import db
from app.models.document import Document
from flask import current_app
from Levenshtein import distance as levenshtein_distance

def get_document_hash(content: str) -> str:
    """Generate a hash of the document content."""
    return hashlib.sha256(content.encode()).hexdigest()

def calculate_levenshtein_similarity(doc1: str, doc2: str) -> float:
    """Calculate normalized Levenshtein similarity between two texts."""
    # Normalize the texts by converting to lowercase and removing extra whitespace
    doc1 = ' '.join(doc1.lower().split())
    doc2 = ' '.join(doc2.lower().split())
    
    # Calculate Levenshtein distance
    dist = levenshtein_distance(doc1, doc2)
    
    # Normalize the distance to a similarity score between 0 and 1
    max_len = max(len(doc1), len(doc2))
    if max_len == 0:
        return 1.0  # Both strings are empty
    
    return 1 - (dist / max_len)

def basic_text_similarity(doc1: str, doc2: str) -> float:
    """Calculate basic TF-IDF similarity between two texts."""
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform([doc1, doc2])
        return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except:
        return 0.0

def ai_powered_similarity(doc1: str, doc2: str) -> float:
    """Calculate similarity using OpenAI embeddings."""
    try:
        if not current_app.config.get('OPENAI_API_KEY'):
            return None

        openai.api_key = current_app.config['OPENAI_API_KEY']
        
        # Get embeddings for both documents
        response1 = openai.embeddings.create(
            model="text-embedding-3-small",
            input=doc1[:8000]  # Limit text length
        )
        response2 = openai.embeddings.create(
            model="text-embedding-3-small",
            input=doc2[:8000]  # Limit text length
        )
        
        # Calculate cosine similarity between embeddings
        embedding1 = np.array(response1.data[0].embedding)
        embedding2 = np.array(response2.data[0].embedding)
        
        similarity = cosine_similarity(
            embedding1.reshape(1, -1),
            embedding2.reshape(1, -1)
        )[0][0]
        
        return float(similarity)
    except:
        return None

def calculate_similarity(document: Document, threshold: float = 0.7) -> List[Tuple[Document, float]]:
    """Calculate similarity between the given document and all other documents."""
    similar_docs = []
    all_docs = Document.query.filter(Document.id != document.id).all()
    
    # First check for exact matches using hash
    exact_matches = [doc for doc in all_docs if doc.content_hash == document.content_hash]
    for match in exact_matches:
        similar_docs.append((match, 1.0))
    
    # If we found exact matches, return them
    if similar_docs:
        return similar_docs
    
    # Try AI-powered similarity if available
    use_ai = bool(current_app.config.get('OPENAI_API_KEY'))
    
    for doc in all_docs:
        # Skip already found exact matches
        if doc in [d[0] for d in similar_docs]:
            continue
        
        # Try AI-powered similarity first
        similarity = None
        if use_ai:
            similarity = ai_powered_similarity(document.content, doc.content)
        
        # Calculate Levenshtein similarity
        levenshtein_sim = calculate_levenshtein_similarity(document.content, doc.content)
        
        # Fall back to basic similarity if AI fails or is not available
        if similarity is None:
            # Combine TF-IDF and Levenshtein similarity
            tfidf_sim = basic_text_similarity(document.content, doc.content)
            similarity = (tfidf_sim + levenshtein_sim) / 2
        else:
            # If AI similarity is available, combine all three
            tfidf_sim = basic_text_similarity(document.content, doc.content)
            similarity = (similarity + tfidf_sim + levenshtein_sim) / 3
        
        if similarity >= threshold:
            similar_docs.append((doc, similarity))
    
    # Sort by similarity score in descending order
    similar_docs.sort(key=lambda x: x[1], reverse=True)
    
    return similar_docs[:5]  # Return top 5 matches 