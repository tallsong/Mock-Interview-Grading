import os

class Config:
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    QUESTIONS_FILE = os.getenv("QUESTIONS_FILE", "data/questions.json")
