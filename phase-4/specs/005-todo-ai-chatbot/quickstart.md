# Quickstart: Todo AI Chatbot (Phase-3)

**Feature Branch**: `005-todo-ai-chatbot`
**Prerequisites**: Phase-2 completed (backend + frontend running)

## Overview

This guide covers the implementation of an AI-powered chat interface for task management. Users can manage their todos through natural language conversation.

## Prerequisites

Before starting implementation:

1. **Backend running**: FastAPI server on port 8080
2. **Frontend running**: Next.js on port 3000
3. **Database configured**: PostgreSQL with existing tasks table
4. **Auth working**: better-auth JWT authentication functional
5. **OpenAI API key**: Required for AI agent

## Quick Setup

### 1. Environment Variables

Add to `backend/.env`:
```bash
OPENAI_API_KEY=sk-your-openai-api-key
```

Add to `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8080/api
```

### 2. Install Dependencies

**Backend:**
```bash
cd backend
pip install openai>=1.0.0 mcp>=1.0.0
```

**Frontend:**
```bash
cd frontend
npm install @chatscope/chat-ui-kit-react
```

### 3. Run Database Migration

```bash
cd backend
alembic revision --autogenerate -m "Add conversation and message tables"
alembic upgrade head
```

## Implementation Order

Follow this sequence for implementation:

### Phase 3.1: Backend Foundation (Priority: Critical)

1. **Add database models** (`backend/app/models/`)
   - Create `conversation.py` with Conversation model
   - Create `message.py` with Message model
   - Update `__init__.py` to export new models

2. **Create MCP tools** (`backend/app/mcp/`)
   - Create `tools.py` with tool implementations
   - Each tool: accept user_id, perform DB operation, return JSON

3. **Create AI agent service** (`backend/app/services/`)
   - Create `agent.py` with OpenAI integration
   - Implement tool calling loop
   - Handle conversation context

### Phase 3.2: Chat API (Priority: Critical)

4. **Create chat routes** (`backend/app/api/routes/chat.py`)
   - POST `/{user_id}/chat` - main chat endpoint
   - GET `/{user_id}/chat/history` - conversation history

5. **Add JWT validation**
   - Reuse existing auth dependency
   - Validate user_id matches JWT

### Phase 3.3: Frontend Chat UI (Priority: High)

6. **Create chat components** (`frontend/src/components/chat/`)
   - ChatContainer - main chat wrapper
   - MessageList - displays conversation
   - MessageInput - user input
   - TypingIndicator - loading state

7. **Create chat page** (`frontend/src/app/(dashboard)/chat/page.tsx`)
   - Replace or augment existing dashboard
   - Integrate ChatKit components

8. **Add API integration** (`frontend/src/lib/chat-api.ts`)
   - sendMessage function
   - getHistory function
   - Handle streaming if needed

### Phase 3.4: Testing & Validation

9. **Backend tests**
   - Unit tests for MCP tools
   - Integration tests for chat endpoint
   - Test conversation persistence

10. **Frontend tests**
    - Component tests for chat UI
    - Integration tests for API calls

## Key Files to Create

```
backend/
├── app/
│   ├── models/
│   │   ├── conversation.py    # NEW
│   │   └── message.py         # NEW
│   ├── mcp/
│   │   ├── __init__.py        # NEW
│   │   └── tools.py           # NEW
│   ├── services/
│   │   └── agent.py           # NEW
│   └── api/routes/
│       └── chat.py            # NEW

frontend/
├── src/
│   ├── components/chat/
│   │   ├── chat-container.tsx # NEW
│   │   ├── message-list.tsx   # NEW
│   │   └── message-input.tsx  # NEW
│   ├── app/(dashboard)/
│   │   └── chat/
│   │       └── page.tsx       # NEW
│   └── lib/
│       └── chat-api.ts        # NEW
```

## Testing the Implementation

### Manual Testing Flow

1. **Start servers:**
   ```bash
   # Terminal 1 - Backend
   cd backend && uvicorn app.main:app --reload --port 8080

   # Terminal 2 - Frontend
   cd frontend && npm run dev
   ```

2. **Open chat interface:**
   - Navigate to http://localhost:3000/dashboard/chat
   - Ensure you're logged in

3. **Test conversation flow:**
   ```
   You: "Add a task to buy groceries"
   AI: "I've added 'buy groceries' to your tasks!"

   You: "What are my tasks?"
   AI: "Here are your tasks: 1. Buy groceries (pending)..."

   You: "Mark groceries as done"
   AI: "Done! I've marked 'buy groceries' as complete."
   ```

4. **Test persistence:**
   - Refresh the page
   - Verify conversation history loads

### Automated Tests

```bash
# Backend tests
cd backend && pytest tests/test_chat.py -v

# Frontend tests
cd frontend && npm test -- --testPathPattern=chat
```

## Common Issues

| Issue | Solution |
|-------|----------|
| OpenAI API errors | Check OPENAI_API_KEY is set correctly |
| JWT validation fails | Ensure token is passed in Authorization header |
| Conversation not persisting | Check database migration ran successfully |
| Chat UI not loading | Verify @chatscope/chat-ui-kit-react installed |
| CORS errors | Check CORS_ORIGINS includes frontend URL |

## Next Steps

After completing implementation:

1. Run full test suite
2. Test on staging environment
3. Performance testing with concurrent users
4. User acceptance testing

Refer to `spec.md` for complete requirements and `data-model.md` for database schema details.
