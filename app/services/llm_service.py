from openai import OpenAI
import json
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        if Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY not set. LLMService will fail if called.")

    def evaluate_answer(self, question_prompt, ideal_answer, user_answer):
        if not self.client:
            raise ValueError("OpenAI API key is not configured.")

        system_prompt = (
            "You are an expert coding interviewer. Your task is to evaluate a candidate's "
            "answer to a coding question against an ideal solution."
        )

        user_message = f"""
Please evaluate the following answer.

Question Prompt: {question_prompt}

Ideal Answer: {ideal_answer}

Candidate Answer: {user_answer}

Tasks:
1. Compare the candidate's answer against the ideal solution.
2. Assign a score from 1 to 5 (1=Poor, 5=Excellent).
3. Provide a 2-3 sentence feedback comment explaining the score.

Return the result as a VALID JSON object with the following keys:
- "score": <int>
- "feedback": <string>

Do not include any markdown formatting (like ```json). Just the raw JSON object.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.0
            )

            content = response.choices[0].message.content.strip()

            # Remove markdown if present (e.g. ```json ... ```)
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)

            # Validate structure
            if "score" not in result or "feedback" not in result:
                raise ValueError("LLM response missing required keys.")

            return {
                "score": int(result["score"]),
                "feedback": str(result["feedback"])
            }

        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response as JSON: {content}")
            raise ValueError("LLM did not return valid JSON.")
        except Exception as e:
            logger.error(f"LLM evaluation failed: {e}")
            raise e
