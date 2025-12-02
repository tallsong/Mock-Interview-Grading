from flask import Flask
from app.config import Config
import json
import os
import logging
from app.models import Question

def load_questions(filepath):
    try:
        if not os.path.exists(filepath):
            print(f"Questions file not found at {filepath}")
            return []
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Convert dicts to Question objects
            return [Question(**q) for q in data]
    except Exception as e:
        print(f"Error loading questions: {e}")
        return []

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Load questions
    app.questions = load_questions(app.config['QUESTIONS_FILE'])
    app.questions_map = {q.id: q for q in app.questions}

    if not app.questions:
        app.logger.warning("No questions loaded! Check data/questions.json.")

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
