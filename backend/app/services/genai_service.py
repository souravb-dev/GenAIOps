import asyncio
import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import httpx
from groq import Groq
from app.core.config import settings
from app.core.exceptions import BaseCustomException, RateLimitError, ExternalServiceError
import logging

logger = logging.getLogger(__name__)

class PromptType(Enum):
    """Types of prompts for different use cases"""
    REMEDIATION = "remediation"
    ANALYSIS = "analysis" 
    EXPLANATION = "explanation"
    OPTIMIZATION = "optimization"
    TROUBLESHOOTING = "troubleshooting"
    CHATBOT = "chatbot"

@dataclass
class GenAIRequest:
    """Data class for GenAI requests"""
    prompt: str
    context: Optional[Dict[str, Any]] = None
    prompt_type: PromptType = PromptType.CHATBOT
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass 
class GenAIResponse:
    """Data class for GenAI responses"""
    content: str
    model: str
    tokens_used: int
    response_time: float
    cached: bool = False
    timestamp: datetime = None
    request_id: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class PromptTemplate:
    """Manages prompt templates for different use cases"""
    
    TEMPLATES = {
        PromptType.REMEDIATION: """
You are an expert cloud operations engineer. Analyze the following issue and provide specific remediation steps.

**Issue Details:**
{issue_details}

**Context:**
- Environment: {environment}
- Service: {service_name}
- Severity: {severity}

**Resource Information:**
{resource_info}

Provide:
1. Root cause analysis
2. Immediate remediation steps
3. Prevention measures
4. Monitoring recommendations

Format your response clearly with actionable steps.
""",
        
        PromptType.ANALYSIS: """
You are a cloud infrastructure analyst. Analyze the following data and provide insights.

**Data to Analyze:**
{data}

**Analysis Context:**
{context}

Provide:
1. Key findings
2. Trends and patterns  
3. Potential issues
4. Recommendations
""",

        PromptType.EXPLANATION: """
You are a technical expert explaining cloud concepts. Explain the following in simple terms.

**Topic:** {topic}
**Context:** {context}
**Audience Level:** {audience_level}

Provide a clear, concise explanation that is easy to understand.
""",

        PromptType.OPTIMIZATION: """
You are a cloud cost and performance optimization expert. Analyze the following resource usage and provide optimization recommendations.

**Resource Data:**
{resource_data}

**Current Costs:**
{cost_data}

**Performance Metrics:**
{performance_data}

Provide:
1. Cost optimization opportunities
2. Performance improvements
3. Resource rightsizing recommendations
4. Implementation priority
""",

        PromptType.TROUBLESHOOTING: """
You are a cloud troubleshooting expert. Help diagnose and resolve the following issue.

**Problem Description:**
{problem}

**Symptoms:**
{symptoms}

**Environment Details:**
{environment}

**Logs/Metrics:**
{logs}

Provide:
1. Diagnostic steps
2. Likely causes
3. Resolution steps
4. Verification methods
""",

        PromptType.CHATBOT: """
You are a helpful cloud operations assistant. Answer the user's question based on the provided context.

**User Question:** {user_input}

**Context:** {context}

**Previous Conversation:** {conversation_history}

Provide a helpful, accurate response. If you need more information, ask clarifying questions.
"""
    }
    
    @classmethod
    def format_prompt(cls, prompt_type: PromptType, **kwargs) -> str:
        """Format a prompt template with provided parameters"""
        template = cls.TEMPLATES.get(prompt_type, cls.TEMPLATES[PromptType.CHATBOT])
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing template parameter: {e}")
            # Return template with available parameters
            available_params = {k: v for k, v in kwargs.items() if f"{{{k}}}" in template}
            return template.format(**available_params)

class ConversationContext:
    """Manages conversation context and history"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for a session"""
        try:
            context_key = f"genai:context:{session_id}"
            context_data = self.redis.get(context_key)
            if context_data:
                return json.loads(context_data)
            return {"messages": [], "metadata": {}}
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {"messages": [], "metadata": {}}
    
    def update_context(self, session_id: str, message: Dict[str, Any], max_messages: int = 10):
        """Update conversation context with new message"""
        try:
            context = self.get_context(session_id)
            context["messages"].append({
                "content": message.get("content", ""),
                "role": message.get("role", "user"),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only recent messages
            if len(context["messages"]) > max_messages:
                context["messages"] = context["messages"][-max_messages:]
            
            context_key = f"genai:context:{session_id}"
            self.redis.setex(
                context_key, 
                timedelta(hours=24), 
                json.dumps(context)
            )
        except Exception as e:
            logger.error(f"Error updating context: {e}")
    
    def clear_context(self, session_id: str):
        """Clear conversation context for a session"""
        try:
            context_key = f"genai:context:{session_id}"
            self.redis.delete(context_key)
        except Exception as e:
            logger.error(f"Error clearing context: {e}")

class GenAIService:
    """Centralized GenAI service for handling AI operations"""
    
    def __init__(self):
        # Initialize Groq client with SSL configuration for corporate networks
        try:
            # Create HTTP client with relaxed SSL for corporate firewalls
            http_client = httpx.Client(
                verify=False,  # Disable SSL verification for corporate networks
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
            
            self.client = Groq(
                api_key=settings.GROQ_API_KEY,
                http_client=http_client
            )
            logger.info("Groq client initialized with custom HTTP configuration")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            # Fallback to basic client
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.redis_client = None
        self.context_manager = None
        self._rate_limiter = {}
        self._batch_queue = []
        self._batch_lock = asyncio.Lock()
        
        if settings.GENAI_ENABLE_CACHING and settings.REDIS_ENABLED:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test the connection
                self.redis_client.ping()
                self.context_manager = ConversationContext(self.redis_client)
                logger.info("GenAI service initialized with Redis caching enabled")
            except Exception as e:
                logger.info(f"Redis not available, running without cache (this is normal for development): {e}")
                self.redis_client = None
        else:
            logger.info("Redis caching disabled in configuration")
    
    def _generate_cache_key(self, request: GenAIRequest) -> str:
        """Generate cache key for request"""
        request_dict = asdict(request)
        # Remove session-specific data for caching
        request_dict.pop("user_id", None)
        request_dict.pop("session_id", None)
        
        # Convert enum to string for JSON serialization
        if "prompt_type" in request_dict and hasattr(request_dict["prompt_type"], "value"):
            request_dict["prompt_type"] = request_dict["prompt_type"].value
        
        request_str = json.dumps(request_dict, sort_keys=True, default=str)
        return f"genai:cache:{hashlib.md5(request_str.encode()).hexdigest()}"
    
    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user is within rate limits"""
        if not user_id:
            return True
            
        current_minute = int(time.time()) // 60
        key = f"{user_id}:{current_minute}"
        
        if key not in self._rate_limiter:
            self._rate_limiter[key] = 0
            
        # Clean old entries
        old_keys = [k for k in self._rate_limiter.keys() 
                   if int(k.split(':')[1]) < current_minute - 1]
        for old_key in old_keys:
            del self._rate_limiter[old_key]
            
        if self._rate_limiter[key] >= settings.GENAI_RATE_LIMIT_PER_MINUTE:
            return False
            
        self._rate_limiter[key] += 1
        return True
    
    def _get_cached_response(self, cache_key: str) -> Optional[GenAIResponse]:
        """Get cached response if available"""
        if not self.redis_client:
            return None
            
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                data["cached"] = True
                return GenAIResponse(**data)
        except Exception as e:
            logger.error(f"Error retrieving cached response: {e}")
        return None
    
    def _cache_response(self, cache_key: str, response: GenAIResponse):
        """Cache the response"""
        if not self.redis_client:
            return
            
        try:
            # Don't cache the "cached" flag itself
            response_dict = asdict(response)
            response_dict["cached"] = False
            response_dict["timestamp"] = response_dict["timestamp"].isoformat()
            
            self.redis_client.setex(
                cache_key,
                timedelta(seconds=settings.GENAI_CACHE_TTL),
                json.dumps(response_dict)
            )
        except Exception as e:
            logger.error(f"Error caching response: {e}")
    
    async def generate_response(self, request: GenAIRequest) -> GenAIResponse:
        """Generate AI response for a single request"""
        start_time = time.time()
        
        # Check rate limiting
        if not self._check_rate_limit(request.user_id):
            raise RateLimitError("Rate limit exceeded. Please try again later.")
        
        # Check cache
        cache_key = self._generate_cache_key(request)
        if settings.GENAI_ENABLE_CACHING:
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                return cached_response
        
        # Prepare request parameters
        model = request.model or settings.GROQ_MODEL
        max_tokens = request.max_tokens or settings.GROQ_MAX_TOKENS
        temperature = request.temperature or settings.GROQ_TEMPERATURE
        
        try:
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": request.prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response = GenAIResponse(
                content=completion.choices[0].message.content,
                model=model,
                tokens_used=completion.usage.total_tokens,
                response_time=time.time() - start_time,
                request_id=f"req_{int(time.time() * 1000)}"
            )
            
            # Cache the response
            if settings.GENAI_ENABLE_CACHING:
                self._cache_response(cache_key, response)
            
            # Update conversation context
            if request.session_id and self.context_manager:
                self.context_manager.update_context(
                    request.session_id,
                    {"role": "user", "content": request.prompt}
                )
                self.context_manager.update_context(
                    request.session_id,
                    {"role": "assistant", "content": response.content}
                )
            
            return response
            
        except Exception as e:
            # Try fallback model if available
            if model != settings.GENAI_FALLBACK_MODEL:
                logger.warning(f"Primary model failed, trying fallback: {e}")
                request.model = settings.GENAI_FALLBACK_MODEL
                try:
                    return await self.generate_response(request)
                except Exception as fallback_error:
                    logger.warning(f"Fallback model also failed: {fallback_error}")
            
            # If both models fail, provide a helpful fallback response
            logger.warning(f"GenAI API error, using fallback response: {e}")
            return GenAIResponse(
                content=self._get_fallback_response(request),
                model="fallback-local",
                tokens_used=0,
                response_time=time.time() - start_time,
                request_id=f"fallback_{int(time.time() * 1000)}"
            )
    
    async def batch_generate(self, requests: List[GenAIRequest]) -> List[GenAIResponse]:
        """Generate responses for multiple requests"""
        if not settings.GENAI_ENABLE_BATCHING or len(requests) == 1:
            return [await self.generate_response(req) for req in requests]
        
        responses = []
        for i in range(0, len(requests), settings.GENAI_BATCH_SIZE):
            batch = requests[i:i + settings.GENAI_BATCH_SIZE]
            batch_responses = await asyncio.gather(*[
                self.generate_response(req) for req in batch
            ])
            responses.extend(batch_responses)
            
            # Small delay between batches to respect rate limits
            if i + settings.GENAI_BATCH_SIZE < len(requests):
                await asyncio.sleep(0.1)
        
        return responses
    
    def generate_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """Generate a formatted prompt using templates"""
        return PromptTemplate.format_prompt(prompt_type, **kwargs)
    
    async def chat_completion(
        self, 
        message: str, 
        session_id: str, 
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> GenAIResponse:
        """Handle chat completion with context management"""
        
        # Get conversation history
        conversation_history = ""
        if self.context_manager:
            ctx = self.context_manager.get_context(session_id)
            recent_messages = ctx.get("messages", [])[-5:]  # Last 5 messages
            conversation_history = "\n".join([
                f"{msg['role']}: {msg['content']}" for msg in recent_messages
            ])
        
        # Format chat prompt
        formatted_prompt = self.generate_prompt(
            PromptType.CHATBOT,
            user_input=message,
            context=json.dumps(context or {}),
            conversation_history=conversation_history
        )
        
        request = GenAIRequest(
            prompt=formatted_prompt,
            context=context,
            prompt_type=PromptType.CHATBOT,
            user_id=user_id,
            session_id=session_id
        )
        
        return await self.generate_response(request)
    
    async def get_remediation_suggestions(
        self,
        issue_details: str,
        environment: str,
        service_name: str,
        severity: str,
        resource_info: Dict[str, Any]
    ) -> GenAIResponse:
        """Get AI-powered remediation suggestions"""
        
        formatted_prompt = self.generate_prompt(
            PromptType.REMEDIATION,
            issue_details=issue_details,
            environment=environment,
            service_name=service_name,
            severity=severity,
            resource_info=json.dumps(resource_info, indent=2)
        )
        
        request = GenAIRequest(
            prompt=formatted_prompt,
            prompt_type=PromptType.REMEDIATION
        )
        
        return await self.generate_response(request)
    
    async def analyze_metrics(
        self,
        data: Dict[str, Any],
        context: str = ""
    ) -> GenAIResponse:
        """Analyze metrics and provide insights"""
        
        formatted_prompt = self.generate_prompt(
            PromptType.ANALYSIS,
            data=json.dumps(data, indent=2),
            context=context
        )
        
        request = GenAIRequest(
            prompt=formatted_prompt,
            prompt_type=PromptType.ANALYSIS
        )
        
        return await self.generate_response(request)
    
    def _get_fallback_response(self, request: GenAIRequest) -> str:
        """Generate a fallback response when AI service is unavailable"""
        base_message = request.prompt.lower()
        
        # Provide helpful responses based on content
        if any(word in base_message for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your CloudOps assistant. I'm currently running in offline mode, but I can still help you with basic information. What would you like to know about your cloud infrastructure?"
        
        if any(word in base_message for word in ['instance', 'server', 'compute']):
            return "I can help you with instance-related queries! Here are some common tasks:\n\n• Check instance status and health\n• Analyze performance metrics\n• Review resource utilization\n• Troubleshoot connectivity issues\n\nFor real-time AI assistance, please ensure the GenAI service is properly configured."
        
        if any(word in base_message for word in ['cost', 'billing', 'expense']):
            return "For cost analysis, I recommend:\n\n• Review your current billing dashboard\n• Check resource usage patterns\n• Look for unused or underutilized resources\n• Consider rightsizing recommendations\n\nI'm currently in offline mode. For detailed AI-powered cost analysis, please check the GenAI service configuration."
        
        if any(word in base_message for word in ['error', 'problem', 'issue', 'down']):
            return "I understand you're experiencing an issue. Here's how I can help:\n\n• Check system logs and monitoring dashboards\n• Review recent changes or deployments\n• Verify service health and connectivity\n• Check resource availability and limits\n\nI'm currently running in offline mode. For advanced AI troubleshooting, please ensure the GenAI service is available."
        
        return "I'm your CloudOps assistant, currently running in offline mode. I can help you with:\n\n• Infrastructure status queries\n• Cost optimization guidance\n• Troubleshooting workflows\n• Best practices recommendations\n\nFor full AI-powered assistance, please check that the GenAI service is properly configured with a valid API key."

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "service": "GenAI Service",
            "provider": "Groq",
            "model": settings.GROQ_MODEL,
            "fallback_model": settings.GENAI_FALLBACK_MODEL,
            "caching_enabled": settings.GENAI_ENABLE_CACHING,
            "batching_enabled": settings.GENAI_ENABLE_BATCHING,
            "rate_limit_per_minute": settings.GENAI_RATE_LIMIT_PER_MINUTE,
            "cache_ttl_seconds": settings.GENAI_CACHE_TTL,
            "supported_prompt_types": [pt.value for pt in PromptType]
        }

# Global service instance
genai_service = GenAIService() 