"""Chat API endpoints for AI-powered task management.

Implements the stateless chat flow:
1. Receive user message
2. Fetch conversation history from DB
3. Store user message
4. Run agent with MCP tools
5. Execute tool calls
6. Store assistant response
7. Return response to frontend
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
    HistoryMessage,
    ToolCallResult,
    ChatErrorResponse,
)
from app.mcp.tools import (
    get_or_create_conversation,
    add_message,
    get_conversation_history,
)
from app.services.agent import generate_response, AIServiceUnavailableError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/{user_id}/chat", tags=["Chat"])


@router.post(
    "",
    response_model=ChatResponse,
    responses={
        400: {"model": ChatErrorResponse, "description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"model": ChatErrorResponse, "description": "Forbidden - user_id mismatch"},
        500: {"model": ChatErrorResponse, "description": "AI service error"},
    },
)
async def send_message(
    user_id: str,
    chat_request: ChatRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> ChatResponse:
    """
    Send a message to the AI chatbot and receive a response.

    The chat flow:
    1. Validates user_id matches authenticated user
    2. Fetches or creates conversation for user
    3. Retrieves conversation history
    4. Stores user message
    5. Generates AI response with tool calling
    6. Stores assistant response
    7. Returns response to client

    - **user_id**: User ID (must match JWT token)
    - **message**: User's natural language message
    """
    # Security: Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )

    # Validate message is not empty
    if not chat_request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    try:
        # Get or create conversation for user
        conversation = await get_or_create_conversation(session, user_id)

        # Get conversation history
        history = await get_conversation_history(session, user_id)

        # Store user message with input method (text or voice)
        await add_message(
            session=session,
            user_id=user_id,
            conversation_id=conversation.id,
            role="user",
            content=chat_request.message,
            input_method=chat_request.input_method,
        )

        # Generate AI response with MCP tool support
        response_text, tool_calls = await generate_response(
            user_id=user_id,
            user_message=chat_request.message,
            history=history,
        )

        # Store assistant response
        await add_message(
            session=session,
            user_id=user_id,
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
        )

        # Convert tool calls to response format
        tool_call_results = None
        if tool_calls:
            tool_call_results = [
                ToolCallResult(tool_name=tc["tool_name"], result=tc["result"])
                for tc in tool_calls
            ]

        return ChatResponse(
            message=response_text,
            tool_calls=tool_call_results,
        )

    except AIServiceUnavailableError as e:
        logger.warning(f"AI service unavailable for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The AI service is temporarily unavailable. Please try again in a moment.",
        )

    except Exception as e:
        logger.error(f"Chat error for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message. Please try again.",
        )


@router.get(
    "/history",
    response_model=ChatHistoryResponse,
    responses={
        401: {"description": "Unauthorized"},
        403: {"model": ChatErrorResponse, "description": "Forbidden - user_id mismatch"},
    },
)
async def get_history(
    user_id: str,
    current_user: CurrentUserDep,
    session: SessionDep,
    limit: int = 50,
) -> ChatHistoryResponse:
    """
    Get conversation history for the user.

    Returns messages in chronological order (oldest first).

    - **user_id**: User ID (must match JWT token)
    - **limit**: Maximum number of messages to return (default: 50)
    """
    # Security: Verify user_id matches authenticated user
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match authenticated user",
        )

    # Get conversation history
    messages = await get_conversation_history(session, user_id, limit=limit)

    # Convert to response format
    history_messages = [
        HistoryMessage(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            input_method=getattr(msg, 'input_method', 'text'),
            created_at=msg.created_at,
        )
        for msg in messages
    ]

    return ChatHistoryResponse(
        messages=history_messages,
        count=len(history_messages),
    )
