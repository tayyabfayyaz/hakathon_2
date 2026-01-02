# Tasks: Todo AI Chatbot (Phase-3)

**Input**: Design documents from `/specs/005-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/
**Generated**: 2026-01-02
**Branch**: `005-todo-ai-chatbot`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` (FastAPI)
- **Frontend**: `frontend/src/` (Next.js 16)
- **Tests**: `backend/tests/`, `frontend/__tests__/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Add OpenAI SDK dependency to backend/requirements.txt (`openai>=1.0.0`)
- [ ] T002 [P] Add MCP SDK dependency to backend/requirements.txt (`mcp>=1.0.0`)
- [ ] T003 [P] Add ChatKit dependency to frontend/package.json (`@chatscope/chat-ui-kit-react`)
- [ ] T004 [P] Add OPENAI_API_KEY to backend/.env.example

**Checkpoint**: Dependencies installed and environment configured

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

### Database Models

- [ ] T005 Create Conversation model in backend/app/models/conversation.py (id, user_id, created_at, updated_at with UNIQUE constraint on user_id)
- [ ] T006 [P] Create MessageRole enum and Message model in backend/app/models/message.py (id, conversation_id, user_id, role, content, created_at)
- [ ] T007 [P] Add description field (Optional[str], max 2000 chars) to Task model in backend/app/models/task.py
- [ ] T008 Export Conversation and Message models in backend/app/models/__init__.py
- [ ] T009 Generate Alembic migration for conversations, messages tables and tasks.description column

### MCP Tools Infrastructure

- [ ] T010 Create MCP module init in backend/app/mcp/__init__.py
- [ ] T011 Create base tool structure with tool definitions schema in backend/app/mcp/tools.py

### Chat Schemas

- [ ] T012 Create ChatRequest, ChatResponse, ToolCallResult schemas in backend/app/schemas/chat.py
- [ ] T013 [P] Create ChatHistoryResponse, HistoryMessage schemas in backend/app/schemas/chat.py
- [ ] T014 [P] Create chat-specific ErrorResponse schemas in backend/app/schemas/chat.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Send Message and Receive AI Response (Priority: P1)

**Goal**: Users can send natural language messages and receive intelligent AI responses with conversation persistence

**Independent Test**: Send "Hello" message, verify AI responds with greeting within 5 seconds, refresh page and verify history loads

### Implementation for User Story 1

- [ ] T015 [US1] Implement get_or_create_conversation function in backend/app/mcp/tools.py
- [ ] T016 [US1] Implement add_message function for storing messages in backend/app/mcp/tools.py
- [ ] T017 [US1] Implement get_conversation_history function in backend/app/mcp/tools.py
- [ ] T018 [US1] Create OpenAI agent service with client initialization in backend/app/services/agent.py
- [ ] T019 [US1] Implement conversation context builder from message history in backend/app/services/agent.py
- [ ] T020 [US1] Implement generate_response function with OpenAI chat completion in backend/app/services/agent.py
- [ ] T021 [US1] Create POST /{user_id}/chat endpoint in backend/app/api/routes/chat.py
- [ ] T022 [US1] Create GET /{user_id}/chat/history endpoint in backend/app/api/routes/chat.py
- [ ] T023 [US1] Add JWT validation and user_id verification to chat routes in backend/app/api/routes/chat.py
- [ ] T024 [US1] Register chat router in backend/app/main.py
- [ ] T025 [US1] Create chat-api.ts client with sendMessage function in frontend/src/lib/chat-api.ts
- [ ] T026 [P] [US1] Create getHistory function in frontend/src/lib/chat-api.ts
- [ ] T027 [US1] Create useChat hook for state management in frontend/src/hooks/use-chat.ts
- [ ] T028 [P] [US1] Create TypingIndicator component in frontend/src/components/chat/typing-indicator.tsx
- [ ] T029 [P] [US1] Create MessageList component with ChatKit in frontend/src/components/chat/message-list.tsx
- [ ] T030 [P] [US1] Create MessageInput component in frontend/src/components/chat/message-input.tsx
- [ ] T031 [US1] Create ChatContainer component wrapping MessageList, MessageInput, TypingIndicator in frontend/src/components/chat/chat-container.tsx
- [ ] T032 [US1] Create chat page at frontend/src/app/(dashboard)/chat/page.tsx
- [ ] T033 [US1] Add navigation link to chat from dashboard navbar in frontend/src/components/layout/navbar.tsx

**Checkpoint**: User Story 1 fully functional - basic chat with AI response works

---

## Phase 4: User Story 2 - Add Task via Natural Language (Priority: P1)

**Goal**: Users can add tasks by describing them naturally (e.g., "Add a task to buy groceries")

**Independent Test**: Say "Add a task to buy groceries", verify task appears in task list

### Implementation for User Story 2

- [ ] T034 [US2] Implement add_task MCP tool function in backend/app/mcp/tools.py (user_id, title, description params)
- [ ] T035 [US2] Add add_task to OpenAI tool definitions in backend/app/services/agent.py
- [ ] T036 [US2] Implement tool calling loop for add_task in backend/app/services/agent.py
- [ ] T037 [US2] Add tool_calls field to ChatResponse in chat endpoint in backend/app/api/routes/chat.py

**Checkpoint**: User Story 2 functional - can add tasks through conversation

---

## Phase 5: User Story 3 - List and View Tasks (Priority: P1)

**Goal**: Users can ask the chatbot to show their tasks (e.g., "What are my tasks?")

**Independent Test**: Ask "Show my tasks", verify AI returns formatted list of tasks

### Implementation for User Story 3

- [ ] T038 [US3] Implement list_tasks MCP tool function in backend/app/mcp/tools.py (user_id, include_completed, limit params)
- [ ] T039 [US3] Add list_tasks to OpenAI tool definitions in backend/app/services/agent.py
- [ ] T040 [US3] Implement tool calling for list_tasks in agent response generation in backend/app/services/agent.py

**Checkpoint**: User Story 3 functional - can view tasks through conversation

---

## Phase 6: User Story 4 - Complete Task via Natural Language (Priority: P2)

**Goal**: Users can mark tasks complete by telling the chatbot (e.g., "I finished buying groceries")

**Independent Test**: Say "Mark buy groceries as done", verify task status updates to completed

### Implementation for User Story 4

- [ ] T041 [US4] Implement complete_task MCP tool function in backend/app/mcp/tools.py (user_id, task_id or task_title params)
- [ ] T042 [US4] Implement task title matching logic for ambiguous references in backend/app/mcp/tools.py
- [ ] T043 [US4] Add complete_task to OpenAI tool definitions in backend/app/services/agent.py
- [ ] T044 [US4] Handle clarification responses when multiple tasks match in backend/app/services/agent.py

**Checkpoint**: User Story 4 functional - can complete tasks through conversation

---

## Phase 7: User Story 5 - Update Task via Natural Language (Priority: P2)

**Goal**: Users can update task details through conversation (e.g., "Change the groceries task to buy vegetables")

**Independent Test**: Say "Update groceries task to add description: get milk", verify task description updates

### Implementation for User Story 5

- [ ] T045 [US5] Implement update_task MCP tool function in backend/app/mcp/tools.py (user_id, task_id/task_title, new_title, new_description params)
- [ ] T046 [US5] Add update_task to OpenAI tool definitions in backend/app/services/agent.py
- [ ] T047 [US5] Handle task identification and update confirmation in backend/app/services/agent.py

**Checkpoint**: User Story 5 functional - can update tasks through conversation

---

## Phase 8: User Story 6 - Delete Task via Natural Language (Priority: P3)

**Goal**: Users can delete tasks through conversation (e.g., "Delete the groceries task")

**Independent Test**: Say "Delete the groceries task", verify task is removed

### Implementation for User Story 6

- [ ] T048 [US6] Implement delete_task MCP tool function in backend/app/mcp/tools.py (user_id, task_id or task_title params)
- [ ] T049 [US6] Add delete_task to OpenAI tool definitions in backend/app/services/agent.py
- [ ] T050 [US6] Handle deletion confirmation in AI response in backend/app/services/agent.py

**Checkpoint**: User Story 6 functional - can delete tasks through conversation

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and improvements across all user stories

### Error Handling

- [ ] T051 Add OpenAI API error handling with retry logic (503 errors) in backend/app/services/agent.py
- [ ] T052 [P] Implement timeout handling (<5s target, show appropriate message) in backend/app/services/agent.py
- [ ] T053 [P] Add graceful degradation when AI service unavailable in backend/app/api/routes/chat.py
- [ ] T054 Handle empty message validation (return 400) in backend/app/api/routes/chat.py
- [ ] T055 [P] Handle long message truncation (max 2000 chars) in backend/app/schemas/chat.py

### Frontend Polish

- [ ] T056 Add error state handling and retry button in frontend/src/components/chat/chat-container.tsx
- [ ] T057 [P] Add message send failure queuing (offline-first) in frontend/src/hooks/use-chat.ts
- [ ] T058 [P] Style chat components to match existing Tailwind/Radix design in frontend/src/components/chat/
- [ ] T059 Add loading skeleton for conversation history in frontend/src/components/chat/message-list.tsx

### Edge Cases

- [ ] T060 Handle non-task-related messages gracefully (guide user to task management) in backend/app/services/agent.py
- [ ] T061 [P] Handle multiple tasks with similar names (ask for clarification) in backend/app/mcp/tools.py
- [ ] T062 Run quickstart.md manual validation flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Phase 3): First to complete - enables basic chat
  - US2 (Phase 4): Can start after US1 - requires tool calling loop
  - US3 (Phase 5): Can start in parallel with US2
  - US4 (Phase 6): Can start after US1-3 foundation
  - US5 (Phase 7): Can start after US1-3 foundation
  - US6 (Phase 8): Can start after US1-3 foundation
- **Polish (Phase 9)**: Depends on US1-6 being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories
- **US2 (P1)**: Depends on US1 (needs tool calling infrastructure)
- **US3 (P1)**: Depends on US1 (needs tool calling infrastructure)
- **US4 (P2)**: Depends on US1 tool infrastructure; independent of US2/US3
- **US5 (P2)**: Depends on US1 tool infrastructure; independent of US2-4
- **US6 (P3)**: Depends on US1 tool infrastructure; independent of US2-5

### Within Each User Story

- Backend MCP tool implementation first
- Add tool to agent definitions
- Implement tool calling in agent
- Frontend updates (if any)

### Parallel Opportunities

- T001-T004 (Setup) can run in parallel
- T005-T009 (Models) can run in parallel after T001-T004
- T010-T014 (MCP/Schemas) can run in parallel
- T028-T030 (Chat UI components) can run in parallel
- T051-T055 (Error handling) can run in parallel
- US4, US5, US6 can run in parallel once US1 completes

---

## Parallel Example: Phase 2 Foundational

```bash
# Launch model creation in parallel:
Task T005: "Create Conversation model in backend/app/models/conversation.py"
Task T006: "Create MessageRole enum and Message model in backend/app/models/message.py"
Task T007: "Add description field to Task model in backend/app/models/task.py"

# After models complete, launch migration:
Task T009: "Generate Alembic migration for new tables"
```

## Parallel Example: User Story 1 Frontend

```bash
# Launch all UI components in parallel:
Task T028: "Create TypingIndicator component"
Task T029: "Create MessageList component"
Task T030: "Create MessageInput component"

# Then compose them:
Task T031: "Create ChatContainer component"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T014)
3. Complete Phase 3: User Story 1 - Basic Chat (T015-T033)
4. Complete Phase 4: User Story 2 - Add Task (T034-T037)
5. Complete Phase 5: User Story 3 - List Tasks (T038-T040)
6. **STOP and VALIDATE**: Test all P1 stories work independently
7. Deploy MVP

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 -> Test independently -> Deploy (Chat works!)
3. Add User Story 2 -> Test independently -> Deploy (Can add tasks!)
4. Add User Story 3 -> Test independently -> Deploy (Can list tasks!) **<- MVP Complete**
5. Add User Story 4 -> Test independently -> Deploy (Can complete tasks!)
6. Add User Story 5 -> Test independently -> Deploy (Can update tasks!)
7. Add User Story 6 -> Test independently -> Deploy (Can delete tasks!)
8. Polish phase -> Final validation

---

## Summary

| Phase | User Story | Priority | Task Count | Key Deliverable |
|-------|-----------|----------|------------|-----------------|
| 1 | Setup | - | 4 | Dependencies installed |
| 2 | Foundational | - | 10 | Models, schemas, MCP base |
| 3 | US1 - Chat & Response | P1 | 19 | Basic AI chat working |
| 4 | US2 - Add Task | P1 | 4 | Create tasks via chat |
| 5 | US3 - List Tasks | P1 | 3 | View tasks via chat |
| 6 | US4 - Complete Task | P2 | 4 | Mark tasks done via chat |
| 7 | US5 - Update Task | P2 | 3 | Modify tasks via chat |
| 8 | US6 - Delete Task | P3 | 3 | Remove tasks via chat |
| 9 | Polish | - | 12 | Error handling, edge cases |
| **Total** | | | **62** | |

### Suggested MVP Scope

- **Phase 1-5 (US1-US3)**: 40 tasks
- **Core functionality**: Send/receive messages, add tasks, list tasks
- **Validates**: Full conversation flow, tool calling, persistence

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All MCP tools must accept `user_id` explicitly (stateless design)
- Frontend uses ChatKit (@chatscope/chat-ui-kit-react)
- Backend uses OpenAI SDK with GPT-4o-mini
