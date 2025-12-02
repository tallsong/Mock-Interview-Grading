import pytest
from app import create_app
from unittest.mock import MagicMock, patch

@pytest.fixture
def app():
    # Mock redis connection to prevent errors during app creation/route import
    with patch('app.services.cache_service.redis.from_url') as mock_redis:
        mock_redis.return_value = MagicMock()

        # Also prevent LLMService from checking API key or failing if not set
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'fake-key'}):
             app = create_app()
             app.config.update({
                 "TESTING": True,
             })
             yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_cache_service():
    with patch('app.routes.cache_service') as mock:
        yield mock

@pytest.fixture
def mock_llm_service():
    with patch('app.routes.llm_service') as mock:
        yield mock
