import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from fuzzywuzzy import fuzz
from typing import Dict, Optional, List

# Download NLTK data if missing at runtime (Django startup or first call will handle it)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')

class FAQMatcher:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.min_similarity_threshold = 0.7  # 70% fuzzy matching threshold
        self.keyword_weight = 0.3
        
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        text = self.preprocess_text(text)
        tokens = word_tokenize(text)
        
        # Remove stopwords and short words
        keywords = [
            token for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        return keywords
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using multiple methods"""
        # Preprocess texts
        text1_clean = self.preprocess_text(text1)
        text2_clean = self.preprocess_text(text2)
        
        if not text1_clean or not text2_clean:
            return 0.0
        
        # Method 1: Token Sort Ratio (good for word order variations)
        token_sort_ratio = fuzz.token_sort_ratio(text1_clean, text2_clean) / 100
        
        # Method 2: Partial Ratio (good for partial matches)
        partial_ratio = fuzz.partial_ratio(text1_clean, text2_clean) / 100
        
        # Method 3: Token Set Ratio (good for longer texts)
        token_set_ratio = fuzz.token_set_ratio(text1_clean, text2_clean) / 100
        
        # Weighted average
        final_score = (token_sort_ratio * 0.4 + 
                      partial_ratio * 0.3 + 
                      token_set_ratio * 0.3)
        
        return final_score
    
    def keyword_match_score(self, user_text: str, faq_keywords: List[str]) -> float:
        """Calculate keyword match score"""
        user_keywords = self.extract_keywords(user_text)
        
        if not user_keywords or not faq_keywords:
            return 0.0
        
        # Check for exact keyword matches
        matches = 0
        for keyword in user_keywords:
            if any(faq_keyword in keyword or keyword in faq_keyword 
                   for faq_keyword in faq_keywords):
                matches += 1
        
        return matches / len(user_keywords) if user_keywords else 0.0
    
    def find_best_match(self, user_query: str) -> Optional[Dict]:
        """Find the best matching FAQ for user query"""
        from faq.models import FAQ
        
        user_query_clean = self.preprocess_text(user_query)
        
        # Get all FAQs
        all_faqs = FAQ.objects.all()
        
        best_match = None
        highest_score = 0
        
        for faq in all_faqs:
            # Calculate text similarity
            text_similarity = self.calculate_similarity(user_query_clean, faq.question)
            
            # Calculate keyword match
            keyword_score = self.keyword_match_score(user_query_clean, faq.keywords)
            
            # Combined score with weights
            combined_score = (text_similarity * (1 - self.keyword_weight) + 
                             keyword_score * self.keyword_weight)
            
            # Boost score if query contains important words
            important_words = ['how', 'what', 'when', 'where', 'why', 'can', 'do', 'is', 'are']
            if any(word in user_query_clean for word in important_words):
                combined_score *= 1.1
            
            if combined_score > highest_score and combined_score >= self.min_similarity_threshold:
                highest_score = combined_score
                best_match = {
                    'faq': faq,
                    'score': combined_score,
                    'text_similarity': text_similarity,
                    'keyword_score': keyword_score
                }
        
        return best_match
    
    def get_response(self, user_query: str) -> Dict:
        """Get response based on user query"""
        match = self.find_best_match(user_query)
        
        if match and match['score'] >= 0.7:  # 70%+ confidence - direct answer
            return {
                'success': True,
                'response': match['faq'].answer,
                'question': match['faq'].question,
                'category': match['faq'].category,
                'confidence': round(match['score'], 2),
                'type': 'faq'
            }
        elif match and match['score'] >= 0.6:  # 60-70% confidence - clarification
            # Ask for clarification or provide partial answer
            return {
                'success': True,
                'response': f"I think you're asking about: {match['faq'].question}\n\n{match['faq'].answer}",
                'question': match['faq'].question,
                'confidence': round(match['score'], 2),
                'type': 'clarification'
            }
        else:
            # No good match found
            return {
                'success': False,
                'response': "I couldn't find a specific answer for your question. Would you like to speak with a human agent for personalized assistance?",
                'type': 'human_handoff_request'
            }
