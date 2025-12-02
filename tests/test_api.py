import json
from unittest.mock import MagicMock

def test_get_questions(client):
    """Test getting all questions."""
    response = client.get('/questions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 5
    assert "id" in data[0]
    assert "prompt" in data[0]

def test_get_question_detail(client):
    """Test getting a specific question."""
    response = client.get('/questions/q1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == 'q1'
    assert "prompt" in data

def test_get_question_not_found(client):
    """Test getting a non-existent question."""
    response = client.get('/questions/nonexistent')
    assert response.status_code == 404

def test_submit_answer_cache_miss(client, mock_cache_service, mock_llm_service):
    """Test submitting an answer with a cache miss (calls LLM)."""
    # Setup mocks
    mock_cache_service.get_evaluation.return_value = None
    mock_llm_service.evaluate_answer.return_value = {
        "score": 5,
        "feedback": "Great job!"
    }

    payload = {
        "question_id": "q1",
        "answer": "def reverse_string(s): return s[::-1]"
    }

    response = client.post('/submit', json=payload)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['score'] == 5
    assert data['feedback'] == "Great job!"
    assert data['cached'] is False

    # Verify calls
    mock_cache_service.get_evaluation.assert_called_once()
    mock_llm_service.evaluate_answer.assert_called_once()
    mock_cache_service.cache_evaluation.assert_called_once()

def test_submit_answer_cache_hit(client, mock_cache_service, mock_llm_service):
    """Test submitting an answer with a cache hit (no LLM call)."""
    # Setup mocks
    mock_cache_service.get_evaluation.return_value = {
        "score": 4,
        "feedback": "Good job."
    }

    payload = {
        "question_id": "q1",
        "answer": "def reverse_string(s): return s[::-1]"
    }

    response = client.post('/submit', json=payload)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['score'] == 4
    assert data['feedback'] == "Good job."
    assert data['cached'] is True

    # Verify calls
    mock_cache_service.get_evaluation.assert_called_once()
    mock_llm_service.evaluate_answer.assert_not_called()

def test_submit_invalid_input(client):
    """Test submitting invalid input."""
    response = client.post('/submit', json={})
    assert response.status_code == 400

    response = client.post('/submit', json={"question_id": "q1"}) # missing answer
    assert response.status_code == 400

def test_submit_question_not_found(client):
    """Test submitting for a non-existent question."""
    payload = {
        "question_id": "nonexistent",
        "answer": "foo"
    }
    response = client.post('/submit', json=payload)
    assert response.status_code == 404
