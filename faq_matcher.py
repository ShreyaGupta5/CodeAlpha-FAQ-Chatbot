"""
FAQ Matcher Module
Vectorizes FAQs and matches user queries using TF-IDF and Cosine Similarity.
"""

import json
import os
import csv
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from nlp_preprocessor import TextPreprocessor


class FAQMatcher:
    """
    NLP engine that uses TF-IDF representation and Cosine Similarity
    to match incoming user questions against a repository of FAQ questions and patterns.
    """

    def __init__(
        self,
        data_path: str = "faq_data.json",
        confidence_threshold: float = 0.25,
        preprocessor: Optional[TextPreprocessor] = None
    ):
        self.data_path = data_path
        self.confidence_threshold = confidence_threshold
        self.preprocessor = preprocessor or TextPreprocessor()
        
        # FAQ database storage
        self.faqs: List[Dict[str, Any]] = []
        self.corpus_texts: List[str] = []
        self.corpus_faq_indices: List[int] = []
        
        # Vectorizer and matrix
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.tfidf_matrix = None
        
        # Load and fit
        self.load_faqs()
        self.build_index()

    def load_faqs(self):
        """Loads FAQs from either JSON or CSV file."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"FAQ file not found at {self.data_path}")

        if self.data_path.endswith('.json'):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.faqs = json.load(f)
        elif self.data_path.endswith('.csv'):
            self.faqs = []
            with open(self.data_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader, start=1):
                    self.faqs.append({
                        "id": idx,
                        "category": row.get("category", "General"),
                        "question": row.get("question", ""),
                        "patterns": [row.get("question", "")],
                        "answer": row.get("answer", "")
                    })
        else:
            raise ValueError("Supported file formats are .json or .csv")

    def build_index(self):
        """
        Extracts questions and alternative phrasing patterns,
        preprocesses each, and fits the TF-IDF vectorizer.
        """
        self.corpus_texts = []
        self.corpus_faq_indices = []

        for idx, item in enumerate(self.faqs):
            # Include main question
            main_q = item.get("question", "")
            preprocessed_main = self.preprocessor.preprocess(main_q)
            if preprocessed_main:
                self.corpus_texts.append(preprocessed_main)
                self.corpus_faq_indices.append(idx)
            
            # Include pattern variants if available
            patterns = item.get("patterns", [])
            for pattern in patterns:
                prep_pattern = self.preprocessor.preprocess(pattern)
                if prep_pattern and prep_pattern != preprocessed_main:
                    self.corpus_texts.append(prep_pattern)
                    self.corpus_faq_indices.append(idx)

        if not self.corpus_texts:
            raise ValueError("Corpus texts are empty. Check your FAQ dataset.")

        # Fit TF-IDF matrix
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_texts)

    def find_match(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Matches a user query against the corpus using cosine similarity.
        Returns the best matching FAQ, confidence score, and alternate suggestions.
        """
        cleaned_query = self.preprocessor.preprocess(query)
        
        # Handle empty/unintelligible query
        if not cleaned_query.strip():
            return {
                "matched": False,
                "confidence": 0.0,
                "answer": "I'm sorry, I couldn't understand that. Could you please rephrase your question?",
                "best_faq": None,
                "suggestions": self.get_popular_suggestions()
            }

        # Vectorize query
        query_vec = self.vectorizer.transform([cleaned_query])
        
        # Compute Cosine Similarities across all corpus items
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        
        # Group scores by FAQ index to find maximum score for each FAQ
        faq_scores: Dict[int, float] = {}
        for score, faq_idx in zip(sim_scores, self.corpus_faq_indices):
            if faq_idx not in faq_scores or score > faq_scores[faq_idx]:
                faq_scores[faq_idx] = float(score)

        # Sort FAQ indices by highest similarity
        sorted_faqs = sorted(faq_scores.items(), key=lambda item: item[1], reverse=True)
        
        if not sorted_faqs:
            return {
                "matched": False,
                "confidence": 0.0,
                "answer": "I couldn't find an answer for that. Please try asking about orders, shipping, returns, or payments.",
                "best_faq": None,
                "suggestions": self.get_popular_suggestions()
            }

        best_faq_idx, best_score = sorted_faqs[0]
        best_faq = self.faqs[best_faq_idx]
        
        # Compile suggestions from top results
        suggestions = []
        for idx, score in sorted_faqs[1:top_k+1]:
            if score > 0.10:
                suggestions.append({
                    "id": self.faqs[idx]["id"],
                    "category": self.faqs[idx]["category"],
                    "question": self.faqs[idx]["question"],
                    "similarity": round(score, 3)
                })

        # Check against threshold
        matched = best_score >= self.confidence_threshold
        
        if matched:
            response_text = best_faq["answer"]
        else:
            response_text = (
                "I am not entirely sure about that. "
                "Did you mean one of the topics below, or would you like to speak to a human representative?"
            )

        return {
            "matched": matched,
            "confidence": round(best_score, 3),
            "answer": response_text,
            "best_faq": {
                "id": best_faq["id"],
                "category": best_faq["category"],
                "question": best_faq["question"]
            } if matched else None,
            "suggestions": suggestions if suggestions else self.get_popular_suggestions()
        }

    def get_popular_suggestions(self, count: int = 3) -> List[Dict[str, Any]]:
        """Returns default popular FAQ suggestions."""
        popular = []
        for faq in self.faqs[:count]:
            popular.append({
                "id": faq["id"],
                "category": faq["category"],
                "question": faq["question"],
                "similarity": 0.0
            })
        return popular


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    faq_path = os.path.join(current_dir, "faq_data.json")
    matcher = FAQMatcher(data_path=faq_path)
    
    test_queries = [
        "How can I track my package?",
        "I want to return an item I bought",
        "Can I pay with credit card or PayPal?",
        "Hello there",
        "What is the meaning of quantum physics?"
    ]
    
    print("\n--- Testing FAQ Matcher ---\n")
    for q in test_queries:
        res = matcher.find_match(q)
        print(f"Query: '{q}'")
        print(f"Matched: {res['matched']} | Confidence: {res['confidence']}")
        print(f"Answer: {res['answer']}")
        print("-" * 50)
