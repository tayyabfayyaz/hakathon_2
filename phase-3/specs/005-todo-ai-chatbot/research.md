# Research: Todo AI Chatbot (Phase-3)

**Feature Branch**: `005-todo-ai-chatbot`
**Date**: 2026-01-02
**Status**: Complete

## Research Areas

### 1. OpenAI Agents SDK Integration

**Decision**: Use OpenAI Agents SDK with GPT-4o-mini model

**Rationale**:
- OpenAI Agents SDK provides built-in tool calling (function calling) support
- GPT-4o-mini offers good balance of cost and capability for task intent parsing
- Native async support works well with FastAPI's async architecture
- Well-documented Python SDK with type hints

**Alternatives Considered**:
- LangChain: More complex, adds unnecessary abstraction layer for this use case
- Direct OpenAI API: Lower-level, would need to implement agent loop manually
- Claude API: Good alternative but user spec explicitly mentions OpenAI

**Implementation Notes**:
- Install: `openai>=1.0.0`
- Use `client.chat.completions.create()` with tools parameter
- Implement tool execution loop for multi-step conversations

---

### 2. MCP (Model Context Protocol) Server Implementation

**Decision**: Use official MCP Python SDK (`mcp>=1.0.0`)

**Rationale**:
- Official SDK ensures protocol compliance
- Provides typed interfaces for tool definitions
- Integrates naturally with OpenAI function calling format
- Stateless tool design aligns with server statelessness requirement

**Alternatives Considered**:
- Custom tool implementation: More work, less standardized
- LangChain tools: Adds dependency overhead

**Implementation Notes**:
- Each MCP tool maps to an OpenAI function definition
- Tools receive `user_id` as explicit parameter (no session state)
- Tools return structured JSON for consistent AI parsing
- Tool schema:
  ```python
  {
    "name": "add_task",
    "description": "Add a new task for the user",
    "parameters": {
      "type": "object",
      "properties": {
        "user_id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string", "optional": True}
      },
      "required": ["user_id", "title"]
    }
  }
  ```

---

### 3. ChatKit UI Component Selection

**Decision**: Use `@chatscope/chat-ui-kit-react` for React chat components

**Rationale**:
- Purpose-built for chat interfaces
- Provides Message, MessageList, MessageInput, TypingIndicator components
- Works with React 19 and Next.js
- Customizable styling to match existing Tailwind/Radix design
- Supports conversation history display

**Alternatives Considered**:
- Build custom components: Time-consuming, reinventing the wheel
- Stream Chat SDK: Overkill, includes backend we don't need
- React Chat Widget: Less customizable

**Implementation Notes**:
- Install: `@chatscope/chat-ui-kit-react`
- Style overrides via CSS modules to match existing design system
- Integrate with TanStack Query for message fetching/sending

---

### 4. Conversation Persistence Strategy

**Decision**: Store conversations and messages in PostgreSQL via SQLModel

**Rationale**:
- Consistent with existing Phase-2 database setup
- SQLModel already in use for Task model
- Relational model fits conversation→messages relationship
- Easy to query conversation history by user_id

**Alternatives Considered**:
- Redis for ephemeral storage: Doesn't persist across restarts
- MongoDB: Adds new database technology
- Client-side storage only: Doesn't meet persistence requirements

**Implementation Notes**:
- Add `Conversation` and `Message` models to backend
- Create Alembic migration for new tables
- Index on `user_id` and `conversation_id` for efficient queries

---

### 5. JWT Authentication for Chat Endpoint

**Decision**: Reuse existing JWT validation from Phase-2 (`better-auth` tokens)

**Rationale**:
- Existing `better-auth` system generates JWTs on frontend
- Backend already has JWT validation for tasks API
- Consistent authentication across all endpoints
- No new authentication system needed

**Alternatives Considered**:
- Separate chat authentication: Adds complexity, inconsistent UX
- API keys: Less secure, harder to manage per-user

**Implementation Notes**:
- Extract `user_id` from JWT in chat endpoint
- Reuse existing `get_current_user` dependency
- Pass `user_id` to all MCP tool calls

---

### 6. Stateless Server Architecture

**Decision**: Full statelessness via database-backed conversation state

**Rationale**:
- Requirement from spec: server must not store in-memory state
- Each request fetches full conversation history from DB
- Enables horizontal scaling without session affinity
- OpenAI handles conversation context via messages array

**Alternatives Considered**:
- In-memory cache with Redis: Adds infrastructure complexity
- Session-based state: Breaks statelessness requirement

**Implementation Notes**:
- Fetch all messages for user's conversation on each request
- Pass conversation history to OpenAI as messages array
- Store new messages before returning response
- Maximum context window management (truncate old messages if needed)

---

### 7. Error Handling and Graceful Degradation

**Decision**: Implement tiered error handling with user-friendly messages

**Rationale**:
- AI service failures should not crash the application
- Users should receive helpful error messages
- Retry logic for transient failures

**Error Categories**:
| Error Type | User Message | Action |
|------------|--------------|--------|
| OpenAI API timeout | "I'm thinking... please wait or try again" | Auto-retry once |
| OpenAI API error | "I'm having trouble right now. Please try again." | Log, return error |
| Tool execution failure | "I couldn't complete that action. [specific reason]" | Return partial result |
| Database error | "Something went wrong. Please try again." | Log, return 500 |
| Invalid input | "I didn't understand that. Could you rephrase?" | Return 400 |

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| AI Model | OpenAI GPT-4o-mini | Latest |
| AI SDK | openai (Python) | >=1.0.0 |
| MCP SDK | mcp (Python) | >=1.0.0 |
| Backend | FastAPI | >=0.115.0 |
| Database | PostgreSQL + SQLModel | Existing |
| Frontend | Next.js 16 + React 19 | Existing |
| Chat UI | @chatscope/chat-ui-kit-react | Latest |
| Auth | better-auth (JWT) | Existing |

---

## Dependencies to Add

### Backend (requirements.txt additions)
```
openai>=1.0.0
mcp>=1.0.0
```

### Frontend (package.json additions)
```json
{
  "@chatscope/chat-ui-kit-react": "^2.0.0"
}
```

---

## Constitution Compliance Notes

| Principle | Compliance |
|-----------|------------|
| Data Integrity First | Messages stored atomically before response |
| Offline-First | Partial - chat requires network; queue failed sends |
| User Experience | <5s response target; loading indicators |
| TDD | Tests required for tools, endpoint, UI |
| Security & Privacy | JWT auth; user_id isolation; no third-party data |
| Performance | Async operations; message pagination if needed |
