import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.genai_service import GenAIService, GenAIRequest, PromptType, GenAIResponse
from app.core.config import settings

# Test client
client = TestClient(app)

# Mock data
MOCK_GROQ_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": "This is a test response from the AI model."
            }
        }
    ],
    "usage": {
        "total_tokens": 25
    }
}

MOCK_USER_TOKEN = "test_token_here"  # In real tests, generate a valid JWT

@pytest.fixture
def mock_auth():
    """Mock authentication for tests"""
    with patch('app.core.permissions.require_auth') as mock:
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"
        mock.return_value = mock_user
        yield mock_user

@pytest.fixture
def genai_service():
    """Create a GenAI service instance for testing"""
    return GenAIService()

@pytest.fixture
def mock_groq_client():
    """Mock Groq client"""
    with patch('groq.Groq') as mock_groq:
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "Test AI response"
        mock_completion.usage.total_tokens = 25
        
        mock_client.chat.completions.create.return_value = mock_completion
        mock_groq.return_value = mock_client
        yield mock_client

class TestGenAIService:
    """Test the GenAI service functionality"""
    
    @pytest.mark.asyncio
    async def test_generate_response_basic(self, genai_service, mock_groq_client):
        """Test basic response generation"""
        request = GenAIRequest(prompt="Hello, how are you?")
        
        response = await genai_service.generate_response(request)
        
        assert isinstance(response, GenAIResponse)
        assert response.content == "Test AI response"
        assert response.tokens_used == 25
        assert response.response_time > 0
        assert not response.cached  # First call shouldn't be cached

    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, genai_service, mock_groq_client):
        """Test response generation with context"""
        request = GenAIRequest(
            prompt="Analyze this issue",
            context={"service": "web-app", "error": "500"},
            prompt_type=PromptType.ANALYSIS,
            user_id="user123",
            session_id="session456"
        )
        
        response = await genai_service.generate_response(request)
        
        assert response.content == "Test AI response"
        assert response.model == settings.GROQ_MODEL

    @pytest.mark.asyncio
    async def test_chat_completion(self, genai_service, mock_groq_client):
        """Test chat completion with conversation context"""
        with patch.object(genai_service, 'context_manager') as mock_context:
            mock_context.get_context.return_value = {"messages": []}
            
            response = await genai_service.chat_completion(
                message="What's the weather like?",
                session_id="test_session",
                user_id="test_user"
            )
            
            assert response.content == "Test AI response"
            mock_context.update_context.assert_called()

    @pytest.mark.asyncio
    async def test_remediation_suggestions(self, genai_service, mock_groq_client):
        """Test remediation suggestions generation"""
        response = await genai_service.get_remediation_suggestions(
            issue_details="Database connection timeout",
            environment="production",
            service_name="api-service",
            severity="high",
            resource_info={"cpu": "80%", "memory": "90%"}
        )
        
        assert response.content == "Test AI response"

    @pytest.mark.asyncio
    async def test_analyze_metrics(self, genai_service, mock_groq_client):
        """Test metrics analysis"""
        test_data = {
            "cpu_usage": [70, 80, 85, 90],
            "memory_usage": [60, 65, 70, 75],
            "response_time": [200, 250, 300, 400]
        }
        
        response = await genai_service.analyze_metrics(
            data=test_data,
            context="Performance analysis for web service"
        )
        
        assert response.content == "Test AI response"

    @pytest.mark.asyncio
    async def test_batch_generate(self, genai_service, mock_groq_client):
        """Test batch generation"""
        requests = [
            GenAIRequest(prompt="Question 1"),
            GenAIRequest(prompt="Question 2"),
            GenAIRequest(prompt="Question 3")
        ]
        
        responses = await genai_service.batch_generate(requests)
        
        assert len(responses) == 3
        for response in responses:
            assert response.content == "Test AI response"

    def test_prompt_template_formatting(self):
        """Test prompt template formatting"""
        from app.services.genai_service import PromptTemplate
        
        formatted = PromptTemplate.format_prompt(
            PromptType.REMEDIATION,
            issue_details="Test issue",
            environment="test",
            service_name="test-service",
            severity="medium",
            resource_info="Test resource info"
        )
        
        assert "Test issue" in formatted
        assert "test-service" in formatted
        assert "medium" in formatted

    def test_rate_limiting(self, genai_service):
        """Test rate limiting functionality"""
        user_id = "test_user"
        
        # Should allow requests within limit
        for i in range(settings.GENAI_RATE_LIMIT_PER_MINUTE):
            assert genai_service._check_rate_limit(user_id) == True
        
        # Should deny request after limit
        assert genai_service._check_rate_limit(user_id) == False

    def test_service_stats(self, genai_service):
        """Test service statistics"""
        stats = genai_service.get_service_stats()
        
        assert stats["service"] == "GenAI Service"
        assert stats["provider"] == "Groq"
        assert stats["model"] == settings.GROQ_MODEL
        assert "supported_prompt_types" in stats

class TestGenAIEndpoints:
    """Test the GenAI API endpoints"""
    
    def test_health_endpoint(self, mock_auth, mock_groq_client):
        """Test the health check endpoint"""
        response = client.get("/api/v1/genai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "GenAI"

    def test_stats_endpoint(self, mock_auth):
        """Test the stats endpoint"""
        with patch('app.api.endpoints.genai.genai_service.get_service_stats') as mock_stats:
            mock_stats.return_value = {
                "service": "GenAI Service",
                "provider": "Groq",
                "model": "llama3-8b-8192"
            }
            
            response = client.get("/api/v1/genai/stats")
            
            assert response.status_code == 200

    def test_chat_endpoint(self, mock_auth, mock_groq_client):
        """Test the chat completion endpoint"""
        with patch('app.api.endpoints.genai.genai_service.chat_completion') as mock_chat:
            mock_response = GenAIResponse(
                content="Hello! How can I help you?",
                model="llama3-8b-8192",
                tokens_used=15,
                response_time=0.5
            )
            mock_chat.return_value = mock_response
            
            response = client.post(
                "/api/v1/genai/chat",
                json={
                    "message": "Hello, AI!",
                    "session_id": "test_session"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "session_id" in data

    def test_remediation_endpoint(self, mock_auth, mock_groq_client):
        """Test the remediation suggestions endpoint"""
        with patch('app.api.endpoints.genai.genai_service.get_remediation_suggestions') as mock_remediation:
            mock_response = GenAIResponse(
                content="1. Check database connections\n2. Restart service\n3. Monitor logs",
                model="llama3-8b-8192",
                tokens_used=50,
                response_time=1.2
            )
            mock_remediation.return_value = mock_response
            
            response = client.post(
                "/api/v1/genai/remediation",
                json={
                    "issue_details": "Database connection timeout",
                    "environment": "production",
                    "service_name": "api-service",
                    "severity": "high",
                    "resource_info": {"cpu": "80%"}
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "remediation_steps" in data

    def test_analysis_endpoint(self, mock_auth, mock_groq_client):
        """Test the data analysis endpoint"""
        with patch('app.api.endpoints.genai.genai_service.analyze_metrics') as mock_analysis:
            mock_response = GenAIResponse(
                content="CPU usage is trending upward. Consider scaling.",
                model="llama3-8b-8192",
                tokens_used=30,
                response_time=0.8
            )
            mock_analysis.return_value = mock_response
            
            response = client.post(
                "/api/v1/genai/analysis",
                json={
                    "data": {"cpu": [70, 80, 90], "memory": [60, 70, 80]},
                    "context": "Performance metrics analysis"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "insights" in data

    def test_custom_prompt_endpoint(self, mock_auth, mock_groq_client):
        """Test the custom prompt endpoint"""
        with patch('app.api.endpoints.genai.genai_service.generate_response') as mock_generate:
            mock_response = GenAIResponse(
                content="Custom response from AI",
                model="llama3-8b-8192",
                tokens_used=20,
                response_time=0.6,
                request_id="req_123"
            )
            mock_generate.return_value = mock_response
            
            response = client.post(
                "/api/v1/genai/custom",
                json={
                    "prompt": "Explain cloud computing",
                    "prompt_type": "explanation",
                    "max_tokens": 100
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data

    def test_batch_endpoint(self, mock_auth, mock_groq_client):
        """Test the batch processing endpoint"""
        with patch('app.api.endpoints.genai.genai_service.batch_generate') as mock_batch:
            mock_responses = [
                GenAIResponse(
                    content=f"Response {i}",
                    model="llama3-8b-8192",
                    tokens_used=10,
                    response_time=0.3,
                    request_id=f"req_{i}"
                )
                for i in range(3)
            ]
            mock_batch.return_value = mock_responses
            
            response = client.post(
                "/api/v1/genai/batch",
                json={
                    "requests": [
                        {"prompt": "Question 1"},
                        {"prompt": "Question 2"},
                        {"prompt": "Question 3"}
                    ]
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3

    def test_context_endpoints(self, mock_auth):
        """Test conversation context endpoints"""
        session_id = "test_session_123"
        
        # Test get context
        with patch('app.api.endpoints.genai.genai_service.context_manager') as mock_context:
            mock_context.get_context.return_value = {
                "messages": [{"role": "user", "content": "Hello"}],
                "metadata": {}
            }
            
            response = client.get(f"/api/v1/genai/context/{session_id}")
            assert response.status_code == 200
            
        # Test clear context
        with patch('app.api.endpoints.genai.genai_service.context_manager') as mock_context:
            response = client.delete(f"/api/v1/genai/context/{session_id}")
            assert response.status_code == 200
            mock_context.clear_context.assert_called_with(session_id)

    def test_prompt_types_endpoint(self, mock_auth):
        """Test the prompt types endpoint"""
        response = client.get("/api/v1/genai/prompts/types")
        
        assert response.status_code == 200
        data = response.json()
        assert "prompt_types" in data
        assert len(data["prompt_types"]) > 0

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_request_data(self, mock_auth):
        """Test handling of invalid request data"""
        response = client.post(
            "/api/v1/genai/chat",
            json={"invalid": "data"}
        )
        
        assert response.status_code == 422  # Validation error

    def test_api_failure_handling(self, mock_auth):
        """Test handling of API failures"""
        with patch('app.api.endpoints.genai.genai_service.generate_response') as mock_generate:
            mock_generate.side_effect = Exception("API Error")
            
            response = client.post(
                "/api/v1/genai/custom",
                json={"prompt": "Test prompt"}
            )
            
            assert response.status_code == 500

    def test_rate_limit_exceeded(self, mock_auth):
        """Test rate limit handling"""
        with patch('app.api.endpoints.genai.genai_service.generate_response') as mock_generate:
            from app.core.exceptions import AppException
            mock_generate.side_effect = AppException("Rate limit exceeded")
            
            response = client.post(
                "/api/v1/genai/custom",
                json={"prompt": "Test prompt"}
            )
            
            assert response.status_code == 500

if __name__ == "__main__":
    # Run basic smoke tests
    print("Running GenAI integration smoke tests...")
    
    try:
        # Test service initialization
        service = GenAIService()
        print("✓ GenAI Service initialized successfully")
        
        # Test configuration
        assert settings.GROQ_API_KEY is not None
        print("✓ Groq API key configured")
        
        # Test prompt template
        from app.services.genai_service import PromptTemplate
        template = PromptTemplate.format_prompt(
            PromptType.CHATBOT,
            user_input="Hello",
            context="{}",
            conversation_history=""
        )
        assert "Hello" in template
        print("✓ Prompt templates working")
        
        # Test service stats
        stats = service.get_service_stats()
        assert stats["service"] == "GenAI Service"
        print("✓ Service stats accessible")
        
        print("\n🎉 All smoke tests passed! GenAI service is ready.")
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        raise 