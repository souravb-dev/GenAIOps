from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from app.services.genai_service import genai_service, GenAIRequest, PromptType
# Rate limiting will be handled by middleware - removing decorator for now
from app.services.auth_service import AuthService
from app.models.user import User
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

class ChatResponse(BaseModel):
    response: str = Field(..., description="AI response")
    session_id: str = Field(..., description="Session ID")
    model: str = Field(..., description="Model used")
    tokens_used: int = Field(..., description="Tokens consumed")
    response_time: float = Field(..., description="Response time in seconds")
    cached: bool = Field(False, description="Whether response was cached")

class RemediationRequest(BaseModel):
    issue_details: str = Field(..., description="Details of the issue")
    environment: str = Field(..., description="Environment name")
    service_name: str = Field(..., description="Service affected")
    severity: str = Field(..., description="Issue severity")
    resource_info: Dict[str, Any] = Field(default_factory=dict, description="Resource information")

class RemediationResponse(BaseModel):
    remediation_steps: str = Field(..., description="AI-generated remediation steps")
    model: str = Field(..., description="Model used")
    tokens_used: int = Field(..., description="Tokens consumed")
    response_time: float = Field(..., description="Response time in seconds")

class AnalysisRequest(BaseModel):
    data: Dict[str, Any] = Field(..., description="Data to analyze")
    context: str = Field("", description="Analysis context")

class AnalysisResponse(BaseModel):
    insights: str = Field(..., description="AI-generated insights")
    model: str = Field(..., description="Model used")
    tokens_used: int = Field(..., description="Tokens consumed")
    response_time: float = Field(..., description="Response time in seconds")

class CustomPromptRequest(BaseModel):
    prompt: str = Field(..., description="Custom prompt")
    prompt_type: PromptType = Field(PromptType.CHATBOT, description="Type of prompt")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens")
    temperature: Optional[float] = Field(None, description="Temperature setting")
    model: Optional[str] = Field(None, description="Specific model to use")

class BatchRequest(BaseModel):
    requests: List[CustomPromptRequest] = Field(..., description="List of requests to process")

class ServiceStats(BaseModel):
    service: str
    provider: str
    model: str
    fallback_model: str
    caching_enabled: bool
    batching_enabled: bool
    rate_limit_per_minute: int
    cache_ttl_seconds: int
    supported_prompt_types: List[str]

@router.get("/health", response_model=Dict[str, str])
async def genai_health():
    """Check GenAI service health"""
    try:
        # Simple test request
        test_request = GenAIRequest(prompt="Say 'OK' if you're working")
        response = await genai_service.generate_response(test_request)
        return {
            "status": "healthy",
            "service": "GenAI",
            "provider": "Groq",
            "test_response": response.content[:50] + "..." if len(response.content) > 50 else response.content
        }
    except Exception as e:
        logger.error(f"GenAI health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"GenAI service unhealthy: {str(e)}"
        )

@router.get("/stats", response_model=ServiceStats)
async def get_service_stats(current_user: User = Depends(AuthService.get_current_user)):
    """Get GenAI service statistics"""
    return genai_service.get_service_stats()

@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Chat completion with conversation context"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        response = await genai_service.chat_completion(
            message=request.message,
            session_id=session_id,
            user_id=str(current_user.id),
            context=request.context
        )
        
        return ChatResponse(
            response=response.content,
            session_id=session_id,
            model=response.model,
            tokens_used=response.tokens_used,
            response_time=response.response_time,
            cached=response.cached
        )
        
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat completion failed: {str(e)}"
        )

@router.post("/remediation", response_model=RemediationResponse)
async def get_remediation_suggestions(
    request: RemediationRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get AI-powered remediation suggestions for issues"""
    try:
        response = await genai_service.get_remediation_suggestions(
            issue_details=request.issue_details,
            environment=request.environment,
            service_name=request.service_name,
            severity=request.severity,
            resource_info=request.resource_info
        )
        
        return RemediationResponse(
            remediation_steps=response.content,
            model=response.model,
            tokens_used=response.tokens_used,
            response_time=response.response_time
        )
        
    except Exception as e:
        logger.error(f"Remediation suggestions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Remediation suggestions failed: {str(e)}"
        )

@router.post("/analysis", response_model=AnalysisResponse)
async def analyze_data(
    request: AnalysisRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Analyze data and provide AI insights"""
    try:
        response = await genai_service.analyze_metrics(
            data=request.data,
            context=request.context
        )
        
        return AnalysisResponse(
            insights=response.content,
            model=response.model,
            tokens_used=response.tokens_used,
            response_time=response.response_time
        )
        
    except Exception as e:
        logger.error(f"Data analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data analysis failed: {str(e)}"
        )

@router.post("/custom", response_model=ChatResponse)
async def custom_prompt(
    request: CustomPromptRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Send a custom prompt to the AI"""
    try:
        genai_request = GenAIRequest(
            prompt=request.prompt,
            prompt_type=request.prompt_type,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            model=request.model,
            user_id=str(current_user.id)
        )
        
        response = await genai_service.generate_response(genai_request)
        
        return ChatResponse(
            response=response.content,
            session_id=f"custom_{response.request_id}",
            model=response.model,
            tokens_used=response.tokens_used,
            response_time=response.response_time,
            cached=response.cached
        )
        
    except Exception as e:
        logger.error(f"Custom prompt error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Custom prompt failed: {str(e)}"
        )

@router.post("/batch", response_model=List[ChatResponse])
async def batch_generate(
    request: BatchRequest,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Process multiple AI requests in batch"""
    try:
        if len(request.requests) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 requests per batch"
            )
        
        genai_requests = [
            GenAIRequest(
                prompt=req.prompt,
                prompt_type=req.prompt_type,
                max_tokens=req.max_tokens,
                temperature=req.temperature,
                model=req.model,
                user_id=str(current_user.id)
            )
            for req in request.requests
        ]
        
        responses = await genai_service.batch_generate(genai_requests)
        
        return [
            ChatResponse(
                response=resp.content,
                session_id=f"batch_{resp.request_id}",
                model=resp.model,
                tokens_used=resp.tokens_used,
                response_time=resp.response_time,
                cached=resp.cached
            )
            for resp in responses
        ]
        
    except Exception as e:
        logger.error(f"Batch generate error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch generation failed: {str(e)}"
        )

@router.delete("/context/{session_id}")
async def clear_conversation_context(
    session_id: str,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Clear conversation context for a session"""
    try:
        if genai_service.context_manager:
            genai_service.context_manager.clear_context(session_id)
        
        return {"message": f"Context cleared for session {session_id}"}
        
    except Exception as e:
        logger.error(f"Clear context error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear context: {str(e)}"
        )

@router.get("/context/{session_id}")
async def get_conversation_context(
    session_id: str,
    current_user: User = Depends(AuthService.get_current_user)
):
    """Get conversation context for a session"""
    try:
        if not genai_service.context_manager:
            return {"messages": [], "metadata": {}}
        
        context = genai_service.context_manager.get_context(session_id)
        return context
        
    except Exception as e:
        logger.error(f"Get context error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get context: {str(e)}"
        )

@router.get("/prompts/types")
async def get_prompt_types(current_user: User = Depends(AuthService.get_current_user)):
    """Get available prompt types"""
    return {
        "prompt_types": [
            {
                "type": pt.value,
                "description": f"Prompt type for {pt.value} use cases"
            }
            for pt in PromptType
        ]
    } 