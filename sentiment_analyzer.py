from textblob import TextBlob
import nltk

# Download required NLTK data (run once)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('brown', quiet=True)
except:
    pass

class SentimentAnalyzer:
    @staticmethod
    def analyze_text(text):
        """Analyze sentiment of text using TextBlob"""
        if not text or text.strip() == '':
            return 0.0
        
        blob = TextBlob(text)
        # Returns polarity score between -1 (negative) and 1 (positive)
        return blob.sentiment.polarity
        # If you get an error, try calling sentiment as a method:
        # return blob.sentiment().polarity
    
    @staticmethod
    def get_sentiment_category(score):
        """Convert sentiment score to category"""
        if score > 0.3:
            return 'Positive'
        elif score < -0.3:
            return 'Negative'
        else:
            return 'Neutral'