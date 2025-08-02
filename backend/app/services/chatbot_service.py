import asyncio
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.chatbot import (
    Conversation, ConversationMessage, ConversationIntent, QueryTemplate,
    ConversationAnalytics, ChatbotFeedback, MessageRole, IntentType, ConversationStatus
)
from app.models.user import User
from app.services.genai_service import genai_service, GenAIRequest, PromptType
from app.schemas.chatbot import (
    IntentResponse, EnhancedChatResponse, ConversationResponse, 
    MessageResponse, TemplateResponse
)
import logging

logger = logging.getLogger(__name__)

class IntentRecognitionService:
    """Service for recognizing user intents from messages"""
    
    # Intent patterns for regex-based recognition
    INTENT_PATTERNS = {
        IntentType.INFRASTRUCTURE_QUERY: [
            r'\b(server|instance|compute|vm|virtual machine)\b',
            r'\b(network|subnet|vcn|vpc)\b',
            r'\b(storage|volume|bucket|object storage)\b',
            r'\b(database|db|autonomous)\b',
            r'\b(load balancer|lb|gateway)\b'
        ],
        IntentType.TROUBLESHOOTING: [
            r'\b(error|issue|problem|fail|down|not working)\b',
            r'\b(troubleshoot|debug|fix|solve|resolve)\b',
            r'\b(crash|hang|timeout|slow)\b',
            r'\b(what\'s wrong|what happened|why)\b'
        ],
        IntentType.MONITORING_ALERT: [
            r'\b(alert|alarm|notification|warning)\b',
            r'\b(metric|cpu|memory|disk|utilization)\b',
            r'\b(threshold|exceeded|high|critical)\b'
        ],
        IntentType.COST_OPTIMIZATION: [
            r'\b(cost|expense|billing|budget)\b',
            r'\b(optimize|reduce|save|cheaper)\b',
            r'\b(usage|consumption|spending)\b'
        ],
        IntentType.REMEDIATION_REQUEST: [
            r'\b(fix|repair|remediate|resolve)\b',
            r'\b(automated|automatic|script)\b',
            r'\b(restart|stop|start|scale)\b'
        ],
        IntentType.RESOURCE_ANALYSIS: [
            r'\b(analyze|analysis|report|overview)\b',
            r'\b(performance|utilization|efficiency)\b',
            r'\b(resources|capacity|usage)\b'
        ],
        IntentType.HELP_REQUEST: [
            r'\b(help|how to|how do|guide|tutorial)\b',
            r'\b(explain|show me|what is|documentation)\b'
        ]
    }
    
    def recognize_intent(self, message: str) -> Tuple[IntentType, float, Dict[str, Any]]:
        """Recognize intent from message using pattern matching"""
        message_lower = message.lower()
        best_intent = IntentType.GENERAL_CHAT
        best_score = 0.1
        entities = {}
        
        # Extract potential entities
        entities.update(self._extract_entities(message))
        
        # Check each intent pattern
        for intent_type, patterns in self.INTENT_PATTERNS.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    matches += 1
                    score += 0.2
            
            # Bonus for multiple pattern matches
            if matches > 1:
                score += 0.3
            
            # Context-based scoring improvements
            if intent_type == IntentType.INFRASTRUCTURE_QUERY and any(
                keyword in message_lower for keyword in ['oci', 'oracle', 'compartment', 'tenancy']
            ):
                score += 0.2
                
            if intent_type == IntentType.TROUBLESHOOTING and any(
                keyword in message_lower for keyword in ['down', 'failing', 'not responding']
            ):
                score += 0.3
            
            if score > best_score:
                best_score = score
                best_intent = intent_type
        
        # Cap confidence at 0.95 for pattern-based recognition
        confidence = min(best_score, 0.95)
        
        return best_intent, confidence, entities
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from message"""
        entities = {}
        
        # Extract OCI-specific entities
        compartment_match = re.search(r'compartment[:\s]+([a-zA-Z0-9\-._]+)', message, re.IGNORECASE)
        if compartment_match:
            entities['compartment_id'] = compartment_match.group(1)
        
        # Extract resource names
        resource_patterns = {
            'instance_name': r'instance[:\s]+([a-zA-Z0-9\-._]+)',
            'service_name': r'service[:\s]+([a-zA-Z0-9\-._]+)',
            'resource_name': r'resource[:\s]+([a-zA-Z0-9\-._]+)'
        }
        
        for entity_type, pattern in resource_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                entities[entity_type] = match.group(1)
        
        return entities

class ChatbotService:
    """Enhanced chatbot service with advanced conversation management"""
    
    def __init__(self):
        self.intent_service = IntentRecognitionService()
        self.default_templates = self._load_default_templates()
    
    async def enhanced_chat(
        self,
        message: str,
        user_id: int,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        oci_context: Optional[Dict[str, Any]] = None,
        enable_intent_recognition: bool = True,
        use_templates: bool = True
    ) -> EnhancedChatResponse:
        """Enhanced chat with full conversation management and intent recognition"""
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        db = next(get_db())
        try:
            # Get or create conversation
            conversation = self._get_or_create_conversation(db, session_id, user_id, context)
            
            # Intent recognition
            intent_response = None
            if enable_intent_recognition:
                intent_type, confidence, entities = self.intent_service.recognize_intent(message)
                intent_response = IntentResponse(
                    intent_type=intent_type,
                    confidence_score=confidence,
                    entities=entities
                )
                
                # Store intent in database
                db_intent = ConversationIntent(
                    conversation_id=conversation.id,
                    intent_type=intent_type,
                    confidence_score=confidence,
                    entities=entities
                )
                db.add(db_intent)
            
            # Enhanced prompt with OCI context
            enhanced_prompt = await self._build_enhanced_prompt(
                message, conversation, oci_context, intent_response
            )
            
            # Generate AI response
            ai_response = await genai_service.chat_completion(
                message=enhanced_prompt,
                session_id=session_id,
                user_id=str(user_id),
                context=context
            )
            
            # Store user message
            user_message = ConversationMessage(
                conversation_id=conversation.id,
                role=MessageRole.USER,
                content=message,
                context_snapshot=context
            )
            db.add(user_message)
            
            # Store AI response
            ai_message = ConversationMessage(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=ai_response.content,
                model_used=ai_response.model,
                tokens_used=ai_response.tokens_used,
                response_time=ai_response.response_time,
                cached=ai_response.cached,
                context_snapshot=oci_context
            )
            db.add(ai_message)
            
            # Update conversation stats
            conversation.total_messages += 2
            conversation.total_tokens_used += ai_response.tokens_used
            conversation.last_activity = datetime.utcnow()
            
            # Update intent message reference
            if intent_response:
                db_intent.message_id = user_message.id
            
            db.commit()
            
            # Get template suggestions
            suggested_templates = []
            if use_templates and intent_response:
                suggested_templates = self._get_template_suggestions(
                    db, intent_response.intent_type, user_id
                )
            
            # Generate OCI insights if context provided
            oci_insights = None
            if oci_context and intent_response and intent_response.intent_type in [
                IntentType.INFRASTRUCTURE_QUERY, IntentType.RESOURCE_ANALYSIS
            ]:
                oci_insights = await self._generate_oci_insights(oci_context)
            
            return EnhancedChatResponse(
                response=ai_response.content,
                session_id=session_id,
                conversation_id=conversation.id,
                model=ai_response.model,
                tokens_used=ai_response.tokens_used,
                response_time=ai_response.response_time,
                cached=ai_response.cached,
                intent=intent_response,
                suggested_templates=suggested_templates,
                oci_insights=oci_insights
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Enhanced chat error: {e}")
            raise
        finally:
            db.close()
    
    def _get_or_create_conversation(
        self, 
        db: Session, 
        session_id: str, 
        user_id: int, 
        context: Optional[Dict[str, Any]]
    ) -> Conversation:
        """Get existing conversation or create new one"""
        conversation = db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                session_id=session_id,
                user_id=user_id,
                context=context,
                status=ConversationStatus.ACTIVE
            )
            db.add(conversation)
            db.flush()  # To get the ID
        
        return conversation
    
    async def _build_enhanced_prompt(
        self,
        message: str,
        conversation: Conversation,
        oci_context: Optional[Dict[str, Any]],
        intent: Optional[IntentResponse]
    ) -> str:
        """Build enhanced prompt with OCI context and conversation history"""
        
        # Base prompt
        enhanced_prompt = f"User message: {message}\n\n"
        
        # Add OCI context if available
        if oci_context:
            enhanced_prompt += f"OCI Context:\n{json.dumps(oci_context, indent=2)}\n\n"
        
        # Add intent context
        if intent and intent.confidence_score > 0.5:
            enhanced_prompt += f"Detected Intent: {intent.intent_type.value} (confidence: {intent.confidence_score:.2f})\n"
            if intent.entities:
                enhanced_prompt += f"Entities: {json.dumps(intent.entities)}\n"
            enhanced_prompt += "\n"
        
        # Add conversation context
        if conversation.context:
            enhanced_prompt += f"Conversation Context: {json.dumps(conversation.context)}\n\n"
        
        # Add system instructions based on intent
        if intent:
            system_instructions = self._get_system_instructions(intent.intent_type)
            enhanced_prompt += f"System Instructions: {system_instructions}\n\n"
        
        enhanced_prompt += f"Provide a helpful response as a cloud operations assistant."
        
        return enhanced_prompt
    
    def _get_system_instructions(self, intent_type: IntentType) -> str:
        """Get system instructions based on intent type"""
        instructions = {
            IntentType.INFRASTRUCTURE_QUERY: "Focus on providing accurate information about cloud infrastructure components, their configurations, and relationships.",
            IntentType.TROUBLESHOOTING: "Analyze the problem systematically, suggest diagnostic steps, and provide clear resolution paths.",
            IntentType.MONITORING_ALERT: "Interpret monitoring data, explain alert conditions, and suggest appropriate responses.",
            IntentType.COST_OPTIMIZATION: "Analyze cost patterns, identify optimization opportunities, and provide actionable recommendations.",
            IntentType.REMEDIATION_REQUEST: "Suggest specific remediation actions, consider safety and approval requirements.",
            IntentType.RESOURCE_ANALYSIS: "Provide comprehensive analysis of resource usage, performance, and optimization opportunities.",
            IntentType.HELP_REQUEST: "Provide clear, step-by-step guidance and educational information."
        }
        return instructions.get(intent_type, "Provide helpful and accurate information.")
    
    def _get_template_suggestions(
        self, 
        db: Session, 
        intent_type: IntentType, 
        user_id: int
    ) -> List[TemplateResponse]:
        """Get relevant template suggestions based on intent"""
        
        # Map intents to categories
        category_map = {
            IntentType.INFRASTRUCTURE_QUERY: "Infrastructure",
            IntentType.TROUBLESHOOTING: "Troubleshooting",
            IntentType.MONITORING_ALERT: "Monitoring",
            IntentType.COST_OPTIMIZATION: "Cost",
            IntentType.REMEDIATION_REQUEST: "Remediation",
            IntentType.RESOURCE_ANALYSIS: "Analysis"
        }
        
        category = category_map.get(intent_type)
        if not category:
            return []
        
        # Get user's role for permission filtering
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        user_roles = [ur.role.name.value for ur in user.user_roles]
        
        # Query templates
        query = db.query(QueryTemplate).filter(
            QueryTemplate.category == category,
            QueryTemplate.is_active == True
        )
        
        # Filter by role requirements
        if 'admin' not in user_roles:
            query = query.filter(
                (QueryTemplate.requires_role.is_(None)) |
                (QueryTemplate.requires_role.in_(user_roles))
            )
        
        templates = query.order_by(desc(QueryTemplate.usage_count)).limit(3).all()
        
        return [
            TemplateResponse(
                id=t.id,
                name=t.name,
                description=t.description,
                category=t.category,
                template_text=t.template_text,
                variables=t.variables,
                usage_count=t.usage_count,
                requires_role=t.requires_role,
                is_active=t.is_active,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in templates
        ]
    
    async def _generate_oci_insights(self, oci_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OCI-specific insights based on context"""
        try:
            # Import OCI services lazily to avoid circular imports
            from app.services.cloud_service import get_cloud_service
            from app.services.monitoring_service import get_monitoring_service
            
            cloud_service = get_cloud_service()
            monitoring_service = get_monitoring_service()
            
            insights = {}
            
            # Get compartment information if available
            if 'compartment_id' in oci_context:
                compartment_id = oci_context['compartment_id']
                
                # Get basic compartment info
                try:
                    compartment_info = await cloud_service.get_compartment_details(compartment_id)
                    insights['compartment'] = compartment_info
                except Exception as e:
                    logger.warning(f"Could not get compartment details: {e}")
                
                # Get current alerts
                try:
                    alerts = await monitoring_service.get_alert_summary(compartment_id)
                    insights['alerts'] = alerts
                except Exception as e:
                    logger.warning(f"Could not get alert summary: {e}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating OCI insights: {e}")
            return {}
    
    def _load_default_templates(self) -> List[Dict[str, Any]]:
        """Load default query templates"""
        return [
            {
                "name": "Check Instance Status",
                "category": "Infrastructure",
                "description": "Check the status of compute instances",
                "template_text": "What is the current status of instance {instance_name} in compartment {compartment_id}?",
                "variables": {"instance_name": "string", "compartment_id": "string"}
            },
            {
                "name": "Analyze High CPU",
                "category": "Troubleshooting",
                "description": "Analyze high CPU utilization",
                "template_text": "Why is {resource_name} showing high CPU utilization and how can I fix it?",
                "variables": {"resource_name": "string"}
            },
            {
                "name": "Cost Analysis",
                "category": "Cost",
                "description": "Analyze costs for a compartment",
                "template_text": "Analyze the costs for compartment {compartment_id} and suggest optimizations",
                "variables": {"compartment_id": "string"}
            },
            {
                "name": "Alert Investigation",
                "category": "Monitoring",
                "description": "Investigate monitoring alerts",
                "template_text": "Investigate the {alert_type} alert for {resource_name} and suggest remediation",
                "variables": {"alert_type": "string", "resource_name": "string"}
            }
        ]

# Global service instance
chatbot_service = ChatbotService() 