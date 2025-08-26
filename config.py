import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
    DATABASE_URL = 'database/messages.db'
    
    # LLM API Configuration (chọn một trong các provider)
    LLM_PROVIDER = 'openrouter'  # 'openai', 'groq', 'openrouter'
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'your-openai-key'
    
    # Groq
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY') or 'gsk_Mi3R'
    
    # OpenRouter
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY') or 'your-openrouter-key'
    
    # Filter thresholds
    NAIVE_BAYES_THRESHOLD = 0.6
    SUSPICIOUS_THRESHOLD = 0.4