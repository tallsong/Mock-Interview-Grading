from flask import Blueprint, jsonify, request, current_app, abort
from app.services.cache_service import CacheService
from app.services.llm_service import LLMService

main_bp = Blueprint('main', __name__)
cache_service = CacheService()
llm_service = LLMService()

@main_bp.route('/questions', methods=['GET'])
def get_questions():
    """Returns a JSON array of all interview questions."""
    questions = current_app.questions
    response = []
    for q in questions:
        response.append({
            "id": q.id,
            "prompt": q.prompt
        })
    return jsonify(response)

@main_bp.route('/questions/<question_id>', methods=['GET'])
def get_question(question_id):
    """Returns the question object for the given id."""
    question = current_app.questions_map.get(question_id)
    if not question:
        abort(404, description="Question not found")

    return jsonify({
        "id": question.id,
        "prompt": question.prompt
    })

@main_bp.route('/submit', methods=['POST'])
def submit_answer():
    """Accepts an answer, evaluates it using LLM or Cache, and returns score + feedback."""
    data = request.get_json()
    if not data:
        abort(400, description="Invalid JSON body")

    if 'question_id' not in data or 'answer' not in data:
        abort(400, description="Missing 'question_id' or 'answer' in request body.")

    question_id = data['question_id']
    user_answer = data['answer']

    question = current_app.questions_map.get(question_id)
    if not question:
        abort(404, description="Question not found")

    # Check cache
    cached_result = cache_service.get_evaluation(question_id, user_answer)
    if cached_result:
        cached_result['cached'] = True
        return jsonify(cached_result)

    # Call LLM
    try:
        result = llm_service.evaluate_answer(
            question_prompt=question.prompt,
            ideal_answer=question.ideal_answer,
            user_answer=user_answer
        )

        # Cache result
        cache_service.cache_evaluation(question_id, user_answer, result)

        result['cached'] = False
        return jsonify(result)

    except ValueError as e:
        # LLM config error or parsing error
        current_app.logger.error(f"Validation/Config error: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
