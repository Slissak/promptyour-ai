"""
Main Chat Service - Orchestrates the complete flow
Coordinates input processing, model selection, prompt generation, and LLM calls
"""
import uuid
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.models.schemas import (
    UserInput,
    QuickInput,
    RawInput,
    ChatResponse,
    QuickResponse,
    RawResponse,
    ProcessedContext,
    ModelChoice,
    LLMRequest,
    UserRating,
)
from backend.app.services.input_processor_v2 import UserInputProcessor
from backend.app.services.model_selector_v2 import ThemeBasedModelSelector
from backend.app.services.prompt_generator import ModelSpecificPromptGenerator
from shared_python.llm_providers.unified_llm_provider import UnifiedLLMProvider
from backend.app.utils.thinking_config import get_recommended_reasoning_params
from backend.app.core.logging import get_logger
from shared_python.usage.usage_service import UsageService
from backend.app.models.user import User
from backend.app.db.database import get_db_session
from backend.app.db.models import Conversation, Message

logger = get_logger(__name__)


class ChatService:
    """Main orchestrator for the AI agentic chat system"""

    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.input_processor = UserInputProcessor()
        self.model_selector = ThemeBasedModelSelector()
        self.prompt_generator = ModelSpecificPromptGenerator()
        self.llm_provider = UnifiedLLMProvider()
        self.usage_service = UsageService(db_session)

    async def process_user_request(
        self,
        user_input: UserInput,
        user_id: str,
        debug_mode: bool = False,
        debug_callback=None,
        connection_id: str = None,
        request_id: str = None,
    ) -> ChatResponse:
        """Main flow: Process user request through complete pipeline"""

        if user_id != "anonymous_user":
            user = await self.db.get(User, uuid.UUID(user_id))
            if not user or not await self.usage_service.check_limits(user):
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Usage limit exceeded")

        if request_id is None:
            request_id = str(uuid.uuid4())

        logger.info(
            "Processing user request",
            request_id=request_id,
            user_id=user_id,
            theme=user_input.theme,
            context=user_input.context,
        )

        try:
            context = await self.input_processor.process_input(user_input)
            model_choice = await self.model_selector.select_model(context)
            conversation_history_str = self._get_conversation_history_str(user_input.message_history)
            system_prompt = await self.prompt_generator.create_model_specific_prompt(
                model=model_choice.model,
                context=context,
                conversation_history=conversation_history_str,
            )
            reasoning_params = get_recommended_reasoning_params(model_choice.model, mode="enhanced")
            llm_request = LLMRequest(
                model=model_choice.model,
                system_prompt=system_prompt,
                user_message=user_input.question,
                max_tokens=4000,
                temperature=0.7,
                **reasoning_params
            )
            llm_response = await self.llm_provider.call_model(llm_request)

            if user_id != "anonymous_user":
                await self.usage_service.increment_usage(user_id, llm_response.cost)

            raw_llm_response = await self.process_raw_request(RawInput(question=user_input.question), user_id)

            # Save to Database if user is authenticated
            if user_id != "anonymous_user":
                try:
                    user_uuid = uuid.UUID(user_id)
                    conversation_uuid = None
                    
                    if user_input.conversation_id:
                        try:
                            conversation_uuid = uuid.UUID(user_input.conversation_id)
                            # Verify ownership
                            result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_uuid, Conversation.user_id == user_uuid))
                            conversation = result.scalars().first()
                            
                            if not conversation:
                                # If provided ID not found, create new
                                conversation = Conversation(id=conversation_uuid, user_id=user_uuid, title=user_input.question[:50])
                                self.db.add(conversation)
                        except ValueError:
                            # Invalid UUID provided
                            pass
                    
                    if not conversation_uuid or (user_input.conversation_id and not conversation):
                         # Double check if we already created it in previous block (conversation might be None if not found)
                         if not user_input.conversation_id or (user_input.conversation_id and not conversation_uuid):
                             conversation_uuid = uuid.uuid4()
                             conversation = Conversation(id=conversation_uuid, user_id=user_uuid, title=user_input.question[:50])
                             self.db.add(conversation)

                    # Create Message
                    # Ensure conversation_uuid is set correctly (either from input or new)
                    if not conversation_uuid and conversation:
                        conversation_uuid = conversation.id
                    
                    message = Message(
                        conversation_id=conversation_uuid,
                        user_message=user_input.question,
                        system_prompt=system_prompt,
                        model_used=llm_response.model,
                        response=llm_response.content,
                        tokens_used=llm_response.tokens_used,
                        cost=llm_response.cost
                    )
                    self.db.add(message)
                    await self.db.commit()
                except Exception as e:
                    logger.error("Failed to save conversation to DB", error=str(e))
                    # Don't fail the request if saving fails, just log it
            
            # Send debug comparison if in debug mode
            if debug_mode and debug_callback:
                comparison_data = {
                    "enhanced_response": {
                        "content": llm_response.content,
                        "tokens_used": llm_response.tokens_used,
                        "cost": llm_response.cost,
                        "response_time_ms": llm_response.response_time_ms,
                        "system_prompt": system_prompt,
                        "reasoning": model_choice.reasoning,
                    },
                    "raw_response": {
                        "content": raw_llm_response.content,
                        "tokens_used": raw_llm_response.tokens_used,
                        "cost": raw_llm_response.cost,
                        "response_time_ms": raw_llm_response.response_time_ms,
                        "system_prompt": "",
                        "user_message": user_input.question,
                    },
                    "model": llm_response.model,
                    "provider": llm_response.provider,
                    "user_question": user_input.question,
                }
                await debug_callback(connection_id, request_id, comparison_data)

            chat_response = ChatResponse(
                content=llm_response.content,
                model_used=llm_response.model,
                provider=llm_response.provider,
                tokens_used=llm_response.tokens_used,
                message_id=llm_response.message_id,
                cost=llm_response.cost,
                response_time_ms=llm_response.response_time_ms,
                reasoning=model_choice.reasoning,
                system_prompt=system_prompt,
                raw_response=raw_llm_response.content,
                raw_tokens_used=raw_llm_response.tokens_used,
                raw_cost=raw_llm_response.cost,
                thinking=llm_response.thinking,
            )

            return chat_response

        except Exception as e:
            logger.error(
                "Request processing failed",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise ChatServiceError(f"Failed to process request: {e}")

    async def process_quick_request(
        self, quick_input: QuickInput, user_id: str, request_id: str = None
    ) -> QuickResponse:
        if user_id != "anonymous_user":
            user = await self.db.get(User, user_id)
            if not user or not await self.usage_service.check_limits(user):
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Usage limit exceeded")

        if request_id is None:
            request_id = str(uuid.uuid4())

        try:
            preferred_model = quick_input.force_model or "nvidia/nemotron-nano-9b-v2:free"
            conversation_history_str = self._get_conversation_history_str(quick_input.message_history)
            system_prompt = self._get_quick_prompt(quick_input.question, conversation_history_str)
            llm_request = LLMRequest(
                model=preferred_model,
                system_prompt=system_prompt,
                user_message=quick_input.question,
                max_tokens=100,
                temperature=0.3,
                enable_reasoning=False,
            )
            llm_response = await self.llm_provider.call_model(llm_request)

            if user_id != "anonymous_user":
                await self.usage_service.increment_usage(user_id, llm_response.cost)

            return QuickResponse(
                content=llm_response.content.strip(),
                model_used=llm_response.model,
                provider=llm_response.provider,
                message_id=llm_response.message_id,
                cost=llm_response.cost,
                response_time_ms=llm_response.response_time_ms,
                system_prompt=system_prompt,
                thinking=llm_response.thinking,
            )

        except Exception as e:
            logger.error(
                "Quick request processing failed",
                request_id=request_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise ChatServiceError(f"Failed to process quick request: {e}")

    def _get_conversation_history_str(self, message_history) -> str:
        if not message_history:
            return ""
        history_lines = []
        for msg in message_history:
            role = "Human" if msg.role == "user" else "Assistant"
            history_lines.append(f"{role}: {msg.content}")
        return "\n\n".join(history_lines)

    def _get_quick_prompt(self, question: str, history: str) -> str:
        from pathlib import Path
        from jinja2 import Environment, FileSystemLoader
        template_dir = Path(__file__).parent.parent / "templates"
        jinja_env = Environment(loader=FileSystemLoader(template_dir))
        quick_template = jinja_env.get_template("quick_response_prompt.j2")
        return quick_template.render(question=question, conversation_history=history)

    async def process_raw_request(
        self, raw_input: "RawInput", user_id: str, request_id: str = None
    ) -> "RawResponse":
        # This is a simplified version for the sake of the refactoring
        # In a real app, this would also have usage checks
        llm_request = LLMRequest(
            model="anthropic/claude-3.5-sonnet",
            system_prompt="",
            user_message=raw_input.question,
            max_tokens=4000,
            temperature=0.7,
            enable_reasoning=False,
        )
        llm_response = await self.llm_provider.call_model(llm_request)
        return RawResponse(
            content=llm_response.content,
            model_used=llm_response.model,
            provider=llm_response.provider,
            tokens_used=llm_response.tokens_used,
            message_id=llm_response.message_id,
            cost=llm_response.cost,
            response_time_ms=llm_response.response_time_ms,
            system_prompt="",
            thinking=llm_response.thinking,
        )

class ChatServiceError(Exception):
    """Exception raised by ChatService"""
    pass
