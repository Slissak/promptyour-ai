"""
Main Chat Service - Orchestrates the complete flow
Coordinates input processing, model selection, prompt generation, and LLM calls
"""
import uuid
from typing import Optional
from datetime import datetime

from app.models.schemas import (
    UserInput, QuickInput, ChatResponse, QuickResponse, ProcessedContext, ModelChoice,
    LLMRequest, UserRating, EvaluationResult
)
from app.services.input_processor_v2 import UserInputProcessor
from app.services.model_selector_v2 import ThemeBasedModelSelector  
from app.services.prompt_generator import ModelSpecificPromptGenerator
from app.integrations.unified_llm_provider import UnifiedLLMProvider
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChatService:
    """Main orchestrator for the AI agentic chat system"""
    
    def __init__(self):
        self.input_processor = UserInputProcessor()
        self.model_selector = ThemeBasedModelSelector()
        self.prompt_generator = ModelSpecificPromptGenerator()
        self.llm_provider = UnifiedLLMProvider()
        
    async def process_user_request(
        self,
        user_input: UserInput,
        user_id: str,
        debug_mode: bool = False,
        debug_callback = None,
        connection_id: str = None,
        request_id: str = None
    ) -> ChatResponse:
        """Main flow: Process user request through complete pipeline"""
        
        if request_id is None:
            request_id = str(uuid.uuid4())
        
        logger.info(
            "Processing user request",
            request_id=request_id,
            user_id=user_id,
            theme=user_input.theme,
            context=user_input.context
        )
        
        try:
            # Step 1: Process and analyze user input
            context = await self.input_processor.process_input(user_input)
            
            logger.info(
                "Input processed", 
                request_id=request_id,
                theme=context.theme,
                inferred_subject=context.inferred_subject,
                inferred_complexity=context.inferred_complexity,
                complexity_score=context.complexity_score
            )
            
            # Step 2: Select optimal model for this context (or use forced model)
            if user_input.force_model and user_input.force_provider:
                # Use forced model for conversation consistency
                model_choice = ModelChoice(
                    model=user_input.force_model,
                    provider=user_input.force_provider,
                    confidence=1.0,  # High confidence since explicitly chosen
                    estimated_cost=0.001,  # Default estimate
                    reasoning=f"Forced to use {user_input.force_model} for conversation consistency"
                )
                
                logger.info(
                    "Using forced model for conversation consistency",
                    request_id=request_id,
                    forced_model=user_input.force_model,
                    forced_provider=user_input.force_provider
                )
            else:
                # Normal model selection process
                model_choice = await self.model_selector.select_model(context)
            
            logger.info(
                "Model selected",
                request_id=request_id,
                selected_model=model_choice.model,
                provider=model_choice.provider,
                confidence=model_choice.confidence,
                estimated_cost=model_choice.estimated_cost
            )
            
            # Step 3: Convert message history to string format for prompt
            conversation_history_str = None
            if user_input.message_history and len(user_input.message_history) > 0:
                history_lines = []
                for msg in user_input.message_history:
                    role = "Human" if msg.role == "user" else "Assistant"
                    history_lines.append(f"{role}: {msg.content}")
                conversation_history_str = "\n\n".join(history_lines)
                
                logger.info(
                    "Using conversation history",
                    request_id=request_id,
                    history_messages=len(user_input.message_history),
                    history_preview=conversation_history_str[:200] + "..." if len(conversation_history_str) > 200 else conversation_history_str
                )
            
            # Step 3: Generate model-specific system prompt
            system_prompt = await self.prompt_generator.create_model_specific_prompt(
                model=model_choice.model,
                context=context,
                conversation_history=conversation_history_str
            )
            
            logger.info(
                "System prompt generated",
                request_id=request_id,
                model=model_choice.model,
                prompt_length=len(system_prompt)
            )
            
            # Note: Debug comparison will be sent after both responses are generated
            
            # Step 4: Call the selected LLM
            llm_request = LLMRequest(
                model=model_choice.model,
                system_prompt=system_prompt,
                user_message=user_input.question,
                max_tokens=4000,
                temperature=0.7
            )
            
            llm_response = await self.llm_provider.call_model(llm_request)
            
            logger.info(
                "LLM response received",
                request_id=request_id,
                model=llm_response.model,
                tokens_used=llm_response.tokens_used,
                actual_cost=llm_response.cost,
                response_time_ms=llm_response.response_time_ms
            )

            # Debug Mode: Get basic response for comparison
            basic_response = None
            if debug_mode and debug_callback and connection_id:
                logger.info("Debug mode: Generating basic response for comparison", request_id=request_id)

                # Create basic LLM request with conversation history but NO system prompt
                # This ensures fair comparison - same context, but no enhanced prompting
                basic_user_message = user_input.question
                if conversation_history_str:
                    basic_user_message = f"{conversation_history_str}\n\nHuman: {user_input.question}"

                basic_llm_request = LLMRequest(
                    model=model_choice.model,
                    system_prompt="",  # No system prompt - raw model response
                    user_message=basic_user_message,
                    max_tokens=4000,
                    temperature=0.7
                )

                basic_llm_response = await self.llm_provider.call_model(basic_llm_request)

                logger.info(
                    "Basic LLM response received for comparison",
                    request_id=request_id,
                    model=basic_llm_response.model,
                    tokens_used=basic_llm_response.tokens_used,
                    actual_cost=basic_llm_response.cost
                )

                # Send comparison data
                comparison_data = {
                    "enhanced_response": {
                        "content": llm_response.content,
                        "tokens_used": llm_response.tokens_used,
                        "cost": llm_response.cost,
                        "response_time_ms": llm_response.response_time_ms,
                        "system_prompt": system_prompt,
                        "reasoning": model_choice.reasoning  # Include model selection reasoning
                    },
                    "basic_response": {
                        "content": basic_llm_response.content,
                        "tokens_used": basic_llm_response.tokens_used,
                        "cost": basic_llm_response.cost,
                        "response_time_ms": basic_llm_response.response_time_ms,
                        "system_prompt": None,  # No system prompt - raw model response
                        "user_message": basic_user_message  # Include the full message sent (with history)
                    },
                    "model": model_choice.model,
                    "provider": model_choice.provider,
                    "user_question": user_input.question
                }
                await debug_callback(connection_id, request_id, comparison_data)

            # Step 5: Store interaction for evaluation (TODO: Implement database storage)
            await self._store_interaction(
                request_id=request_id,
                user_id=user_id,
                context=context,
                model_choice=model_choice,
                llm_response=llm_response,
                system_prompt=system_prompt
            )
            
            # Step 6: Return response to user
            chat_response = ChatResponse(
                content=llm_response.content,
                model_used=llm_response.model,
                provider=llm_response.provider,
                message_id=llm_response.message_id,
                cost=llm_response.cost,
                response_time_ms=llm_response.response_time_ms,
                reasoning=model_choice.reasoning,
                system_prompt=system_prompt
            )
            
            logger.info(
                "Request completed successfully",
                request_id=request_id,
                message_id=chat_response.message_id,
                final_cost=chat_response.cost
            )
            
            return chat_response
            
        except Exception as e:
            logger.error(
                "Request processing failed",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise ChatServiceError(f"Failed to process request: {e}")

    async def process_quick_request(
        self,
        quick_input: QuickInput,
        user_id: str,
        request_id: str = None
    ) -> QuickResponse:
        """Process quick one-liner request - simplified flow without theme/audience selection"""

        if request_id is None:
            request_id = str(uuid.uuid4())

        logger.info(
            "Processing quick request",
            request_id=request_id,
            user_id=user_id,
            question_length=len(quick_input.question)
        )

        try:
            # Step 1: Select fast, cost-effective model for quick responses
            # Prioritize speed and cost over complex reasoning
            preferred_model = quick_input.force_model or "claude-3-haiku"
            preferred_provider = quick_input.force_provider or "anthropic"

            # Step 2: Process conversation history for context
            conversation_history_str = ""
            if quick_input.message_history:
                history_lines = []
                for msg in quick_input.message_history:
                    role = "Human" if msg.role == "user" else "Assistant"
                    history_lines.append(f"{role}: {msg.content}")
                conversation_history_str = "\n".join(history_lines)

                logger.info(
                    "Using conversation history in quick mode",
                    request_id=request_id,
                    history_messages=len(quick_input.message_history),
                    history_preview=conversation_history_str[:200] + "..." if len(conversation_history_str) > 200 else conversation_history_str
                )

            # Step 3: Generate simple system prompt for one-liner with history
            from pathlib import Path
            from jinja2 import Environment, FileSystemLoader

            template_dir = Path(__file__).parent.parent / "templates"
            jinja_env = Environment(loader=FileSystemLoader(template_dir))
            quick_template = jinja_env.get_template("quick_response_prompt.j2")
            system_prompt = quick_template.render(
                question=quick_input.question,
                conversation_history=conversation_history_str
            )

            logger.info(
                "Quick system prompt generated",
                request_id=request_id,
                prompt_length=len(system_prompt)
            )

            # Step 4: Call LLM with minimal configuration
            llm_request = LLMRequest(
                model=preferred_model,
                system_prompt=system_prompt,
                user_message=quick_input.question,
                max_tokens=100,  # Keep it short
                temperature=0.3  # Lower creativity for more direct answers
            )

            llm_response = await self.llm_provider.call_model(llm_request)

            logger.info(
                "Quick LLM response received",
                request_id=request_id,
                model=llm_response.model,
                tokens_used=llm_response.tokens_used,
                cost=llm_response.cost,
                response_time_ms=llm_response.response_time_ms
            )

            # Step 5: Return quick response
            quick_response = QuickResponse(
                content=llm_response.content.strip(),
                model_used=llm_response.model,
                provider=llm_response.provider,
                message_id=llm_response.message_id,
                cost=llm_response.cost,
                response_time_ms=llm_response.response_time_ms,
                system_prompt=system_prompt
            )

            logger.info(
                "Quick request completed",
                request_id=request_id,
                message_id=quick_response.message_id,
                final_cost=quick_response.cost
            )

            return quick_response

        except Exception as e:
            logger.error(
                "Quick request processing failed",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise ChatServiceError(f"Failed to process quick request: {e}")

    async def collect_user_rating(
        self, 
        rating: UserRating,
        user_id: str
    ) -> bool:
        """Collect and store user feedback"""
        
        logger.info(
            "Collecting user rating",
            message_id=rating.message_id,
            user_id=user_id,
            rating=rating.rating
        )
        
        try:
            # TODO: Store rating in database
            await self._store_user_rating(rating, user_id)
            
            # TODO: Trigger evaluation pipeline if needed
            await self._trigger_evaluation_update(rating.message_id)
            
            logger.info(
                "User rating stored successfully",
                message_id=rating.message_id,
                rating=rating.rating
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to store user rating",
                message_id=rating.message_id,
                error=str(e)
            )
            return False

    async def get_conversation_history(
        self, 
        conversation_id: str, 
        user_id: str,
        limit: int = 10
    ) -> list:
        """Get conversation history for context"""
        
        logger.info(
            "Fetching conversation history",
            conversation_id=conversation_id,
            user_id=user_id,
            limit=limit
        )
        
        # TODO: Implement database query for conversation history
        return []

    async def _store_interaction(
        self,
        request_id: str,
        user_id: str,
        context: ProcessedContext,
        model_choice,
        llm_response,
        system_prompt: str
    ):
        """Store interaction data for evaluation and learning"""
        
        interaction_data = {
            "request_id": request_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "context": {
                "theme": context.theme.value,
                "inferred_subject": context.inferred_subject,
                "inferred_complexity": context.inferred_complexity,
                "complexity_score": context.complexity_score,
                "question": context.question,
                "context": context.context
            },
            "model_selection": {
                "selected_model": model_choice.model,
                "provider": model_choice.provider,
                "confidence": model_choice.confidence,
                "reasoning": model_choice.reasoning,
                "estimated_cost": model_choice.estimated_cost
            },
            "system_prompt": system_prompt,
            "response": {
                "content": llm_response.content,
                "tokens_used": llm_response.tokens_used,
                "actual_cost": llm_response.cost,
                "response_time_ms": llm_response.response_time_ms,
                "message_id": llm_response.message_id
            }
        }
        
        # TODO: Store in database
        logger.info("Interaction data prepared for storage", request_id=request_id)

    async def _store_user_rating(self, rating: UserRating, user_id: str):
        """Store user rating in database"""
        # TODO: Implement database storage
        logger.info("User rating prepared for storage", message_id=rating.message_id)

    async def _trigger_evaluation_update(self, message_id: str):
        """Trigger evaluation pipeline update"""
        # TODO: Implement evaluation trigger
        logger.info("Evaluation update triggered", message_id=message_id)

    async def health_check(self) -> dict:
        """Check health of all service components"""
        
        health_status = {
            "service": "healthy",
            "components": {}
        }
        
        # Check LLM provider health
        try:
            openrouter_healthy = await self.llm_provider.health_check()
            health_status["components"]["openrouter"] = "healthy" if openrouter_healthy else "unhealthy"
        except Exception as e:
            health_status["components"]["openrouter"] = f"error: {e}"
        
        # Check other components
        health_status["components"]["input_processor"] = "healthy" 
        health_status["components"]["model_selector"] = "healthy"
        health_status["components"]["prompt_generator"] = "healthy"
        
        # Overall health
        if any("unhealthy" in status or "error" in status for status in health_status["components"].values()):
            health_status["service"] = "degraded"
        
        return health_status


class ChatServiceError(Exception):
    """Exception raised by ChatService"""
    pass