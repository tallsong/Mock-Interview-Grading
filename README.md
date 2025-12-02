# Mock Interview Grading Microservice

This is a RESTful microservice built with Flask that allows clients to fetch coding interview questions, submit answers, and receive automated evaluations (score + feedback) powered by an LLM (OpenAI GPT). Caching is implemented using Redis to minimize redundant LLM calls.

## Prerequisites

- Docker and Docker Compose
- An OpenAI API Key

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Environment Variables:**
   Create a `.env` file in the root directory (optional, but recommended for local dev) or pass variables directly to docker-compose.

   The following environment variables are used:
   - `OPENAI_API_KEY`: Your OpenAI API Key (Required for LLM features).
   - `REDIS_URL`: URL for Redis connection (Defaults to `redis://redis:6379/0` in Docker).

3. **Build and Run with Docker Compose:**

   Run the following command to build the Docker image and start the Flask service and Redis:

   ```bash
   export OPENAI_API_KEY=your_actual_api_key_here
   docker-compose up --build
   ```

   The service will be available at `http://localhost:5000`.

## API Usage

### 1. Get All Questions

Fetches the list of available coding questions.

**Request:**
```bash
curl -X GET http://localhost:5000/questions
```

**Response:**
```json
[
  {
    "id": "q1",
    "prompt": "Write a function to reverse a string in Python."
  },
  ...
]
```

### 2. Get Specific Question

Fetches details for a specific question ID.

**Request:**
```bash
curl -X GET http://localhost:5000/questions/q1
```

**Response:**
```json
{
  "id": "q1",
  "prompt": "Write a function to reverse a string in Python."
}
```

### 3. Submit Answer

Submits an answer for evaluation. Checks Redis cache first; calls OpenAI API on cache miss.

**Request:**
```bash
curl -X POST http://localhost:5000/submit \
  -H "Content-Type: application/json" \
  -d '{
        "question_id": "q1",
        "answer": "def reverse_string(s): return s[::-1]"
      }'
```

**Response:**
```json
{
  "score": 5,
  "feedback": "The solution is correct and pythonic.",
  "cached": false
}
```

If you submit the same request again, you should see `"cached": true`.

## Running Tests

To run the test suite, you can use `pytest`. The tests mock the OpenAI API and Redis, so no real API key or running Redis instance is required.

1. **Install dependencies locally:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run tests:**
   ```bash
   PYTHONPATH=. pytest
   ```

## Project Structure

- `app/`: Contains the Flask application code.
  - `services/`: Logic for Redis (`cache_service.py`) and OpenAI (`llm_service.py`).
  - `routes.py`: API endpoint definitions.
- `data/questions.json`: The database of interview questions.
- `tests/`: Pytest unit tests.
- `Dockerfile` & `docker-compose.yml`: Containerization configuration.
