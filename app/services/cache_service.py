import redis
import hashlib
import json
import logging
from app.config import Config

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        try:
            self.redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
            self.ttl = 3600  # 1 hour
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def _generate_key(self, question_id, answer):
        answer_hash = hashlib.sha256(answer.encode('utf-8')).hexdigest()
        return f"grading:{question_id}:{answer_hash}"

    def get_evaluation(self, question_id, answer):
        if not self.redis_client:
            return None

        try:
            key = self._generate_key(question_id, answer)
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Error reading from Redis: {e}")
        return None

    def cache_evaluation(self, question_id, answer, result):
        if not self.redis_client:
            return

        try:
            key = self._generate_key(question_id, answer)
            self.redis_client.setex(key, self.ttl, json.dumps(result))
        except Exception as e:
            logger.error(f"Error writing to Redis: {e}")
