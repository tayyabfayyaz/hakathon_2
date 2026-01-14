# Tasks: Todo AI Chatbot (Phase-3) - MCP SDK Implementation

**Input**: Design documents from `/specs/005-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/
**Generated**: 2026-01-09
**Branch**: `005-todo-ai-chatbot`

## Overview

This task list implements the AI chatbot using the **Official MCP SDK** instead of OpenAI function calling. The MCP server exposes stateless tools for task operations that integrate with the AI agent.

### Key Changes from Previous Implementation
- **Remove**: OpenAI function calling format in `backend/app/mcp/tools.py`
- **Remove**: `TOOL_DEFINITIONS` OpenAI-style schema in `backend/app/services/agent.py`
- **Add**: Official MCP SDK server implementation
- **Add**: MCP client integration in agent service
- **Tools**: add_task, update_task, list_tasks, complete_task_toggle, delete_task

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` (FastAPI)
- **Frontend**: `frontend/src/` (Next.js 16)
- **Tests**: `backend/tests/`, `frontend/__tests__/`

---

## Phase 1: Setup & Cleanup (Remove OpenAI Function Calling)

**Purpose**: Remove existing OpenAI function calling and prepare for MCP SDK implementation

### Cleanup Tasks

- [X] T001 Remove OpenAI-style TOOL_DEFINITIONS from backend/app/mcp/tools.py (lines 19-135)
- [X] T002 [P] Remove OpenAI-style TOOL_DEFINITIONS from backend/app/services/agent.py (lines 53-167)
- [X] T003 [P] Remove tool_choice="auto" from _call_gemini_with_retry in backend/app/services/agent.py
- [X] T004 Update backend/requirements.txt to ensure mcp>=1.0.0 is properly configured for MCP SDK server

### New Dependencies

- [X] T005 Add mcp[server]>=1.0.0 to backend/requirements.txt for MCP server capabilities
- [X] T006 [P] Add httpx>=0.27.0 to backend/requirements.txt for MCP client HTTP transport

**Checkpoint**: OpenAI function calling removed, ready for MCP SDK implementation

---

## Phase 2: MCP Server Implementation (Official SDK)

**Purpose**: Build MCP server with official SDK exposing todo tools

### MCP Server Core

- [X] T007 Create MCP server module structure in backend/app/mcp/server.py with FastMCP initialization
- [X] T008 Configure MCP server with name "todo-mcp-server" and version in backend/app/mcp/server.py
- [X] T009 [P] Create tool result types (ToolResult dataclass) in backend/app/mcp/types.py

### MCP Tool Implementations (5 tools)

- [X] T010 Implement add_task MCP tool using @mcp.tool() decorator in backend/app/mcp/server.py (params: user_id, title, description optional; returns: success, task object)

- [X] T011 [P] Implement list_tasks MCP tool using @mcp.tool() decorator in backend/app/mcp/server.py (params: user_id, include_completed bool, limit int; returns: success, tasks array, count)

- [X] T012 [P] Implement update_task MCP tool using @mcp.tool() decorator in backend/app/mcp/server.py (params: user_id, task_id optional, task_title optional, new_title optional, new_description optional; returns: success, updated task)

- [X] T013 [P] Implement complete_task_toggle MCP tool using @mcp.tool() decorator in backend/app/mcp/server.py (params: user_id, task_id optional, task_title optional; returns: success, task with toggled completed state)

- [X] T014 [P] Implement delete_task MCP tool using @mcp.tool() decorator in backend/app/mcp/server.py (params: user_id, task_id optional, task_title optional; returns: success, deleted task message)

### MCP Server Integration

- [X] T015 Create database session factory for MCP tools in backend/app/mcp/server.py
- [X] T016 Export MCP server instance in backend/app/mcp/__init__.py
- [X] T017 Add MCP server startup to FastAPI lifespan in backend/app/main.py

**Checkpoint**: MCP server running with 5 tools exposed via official SDK

---

## Phase 3: Agent Service Refactor (MCP Client Integration)

**Purpose**: Refactor agent service to use MCP client for tool calls instead of OpenAI function calling

### MCP Client Setup

- [X] T018 Create MCP client wrapper in backend/app/services/mcp_client.py
- [X] T019 Implement tool discovery (list available tools from MCP server) in backend/app/services/mcp_client.py
- [X] T020 Implement tool execution method (call_tool) in backend/app/services/mcp_client.py

### Agent Service Refactor

- [X] T021 Remove tool calling loop from generate_response in backend/app/services/agent.py
- [X] T022 Add MCP client initialization to AgentService.__init__ in backend/app/services/agent.py
- [X] T023 Implement intent detection for tool routing in backend/app/services/agent.py
- [X] T024 Implement tool result formatting for AI context in backend/app/services/agent.py
- [X] T025 Update generate_response to use MCP tools via client in backend/app/services/agent.py
- [X] T026 Update _demo_mode_response to use MCP client for fallback in backend/app/services/agent.py

**Checkpoint**: Agent service uses MCP client to call tools from MCP server

---

## Phase 4: User Story 1 - Send Message and Receive AI Response (Priority: P1)

**Goal**: Users can send natural language messages and receive intelligent AI responses with conversation persistence

**Independent Test**: Send "Hello" message, verify AI responds with greeting within 5 seconds, refresh page and verify history loads

### Backend Implementation

- [X] T027 [US1] Verify conversation persistence functions work in backend/app/mcp/tools.py (get_or_create_conversation, add_message, get_conversation_history)
- [X] T028 [US1] Update POST /{user_id}/chat endpoint to use MCP-based agent in backend/app/api/routes/chat.py
- [X] T029 [US1] Update GET /{user_id}/chat/history endpoint response format in backend/app/api/routes/chat.py

### Frontend Implementation (ChatKit UI)

- [X] T030 [P] [US1] Verify ChatKit TypingIndicator component in frontend/src/components/chat/typing-indicator.tsx
- [X] T031 [P] [US1] Verify ChatKit MessageList component in frontend/src/components/chat/message-list.tsx
- [X] T032 [P] [US1] Verify ChatKit MessageInput component in frontend/src/components/chat/message-input.tsx
- [X] T033 [US1] Verify ChatContainer integration in frontend/src/components/chat/chat-container.tsx
- [X] T034 [US1] Verify chat page at frontend/src/app/(dashboard)/chat/page.tsx
- [X] T035 [US1] Verify useChat hook state management in frontend/src/hooks/use-chat.ts

**Checkpoint**: User Story 1 fully functional - basic chat with AI response works via MCP

---

## Phase 5: User Story 2 - Add Task via Natural Language (Priority: P1)

**Goal**: Users can add tasks by describing them naturally (e.g., "Add a task to buy groceries")

**Independent Test**: Say "Add a task to buy groceries", verify task appears in task list

### Implementation

- [X] T036 [US2] Test add_task MCP tool integration via chat endpoint
- [X] T037 [US2] Verify intent detection routes "add/create/remind" keywords to add_task tool in backend/app/services/agent.py
- [X] T038 [US2] Verify AI confirmation message after task creation

**Checkpoint**: User Story 2 functional - can add tasks through conversation via MCP

---

## Phase 6: User Story 3 - List and View Tasks (Priority: P1)

**Goal**: Users can ask the chatbot to show their tasks (e.g., "What are my tasks?")

**Independent Test**: Ask "Show my tasks", verify AI returns formatted list of tasks

### Implementation

- [X] T039 [US3] Test list_tasks MCP tool integration via chat endpoint
- [X] T040 [US3] Verify intent detection routes "show/list/what tasks" keywords to list_tasks tool in backend/app/services/agent.py
- [X] T041 [US3] Verify AI formats task list in readable response

**Checkpoint**: User Story 3 functional - can view tasks through conversation via MCP

---

## Phase 7: User Story 4 - Toggle Task Completion (Priority: P2)

**Goal**: Users can toggle task completion by telling the chatbot (e.g., "Mark buy groceries as done" or "Unmark groceries")

**Independent Test**: Say "Mark buy groceries as done", verify task status toggles

### Implementation

- [X] T042 [US4] Test complete_task_toggle MCP tool integration via chat endpoint
- [X] T043 [US4] Verify intent detection routes "done/finished/complete/unmark" keywords to complete_task_toggle tool
- [X] T044 [US4] Implement task title fuzzy matching in complete_task_toggle tool in backend/app/mcp/server.py
- [X] T045 [US4] Handle clarification when multiple tasks match title in backend/app/services/agent.py

**Checkpoint**: User Story 4 functional - can toggle task completion through conversation via MCP

---

## Phase 8: User Story 5 - Update Task via Natural Language (Priority: P2)

**Goal**: Users can update task details through conversation (e.g., "Change the groceries task to buy vegetables")

**Independent Test**: Say "Update groceries task to add description: get milk", verify task updates

### Implementation

- [X] T046 [US5] Test update_task MCP tool integration via chat endpoint
- [X] T047 [US5] Verify intent detection routes "change/update/rename/edit" keywords to update_task tool
- [X] T048 [US5] Verify AI confirmation message after task update

**Checkpoint**: User Story 5 functional - can update tasks through conversation via MCP

---

## Phase 9: User Story 6 - Delete Task via Natural Language (Priority: P3)

**Goal**: Users can delete tasks through conversation (e.g., "Delete the groceries task")

**Independent Test**: Say "Delete the groceries task", verify task is removed

### Implementation

- [X] T049 [US6] Test delete_task MCP tool integration via chat endpoint
- [X] T050 [US6] Verify intent detection routes "delete/remove/get rid" keywords to delete_task tool
- [X] T051 [US6] Verify AI confirmation message after task deletion

**Checkpoint**: User Story 6 functional - can delete tasks through conversation via MCP

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and improvements across all user stories

### Error Handling

- [X] T052 Add MCP server error handling with graceful degradation in backend/app/mcp/server.py
- [X] T053 [P] Add MCP client timeout handling (5s target) in backend/app/services/mcp_client.py
- [X] T054 [P] Update agent error messages for MCP failures in backend/app/services/agent.py
- [X] T055 Handle empty message validation (return 400) in backend/app/api/routes/chat.py

### Frontend Polish

- [X] T056 Add error state handling for MCP failures in frontend/src/components/chat/chat-container.tsx
- [X] T057 [P] Style ChatKit components to match existing Tailwind/Radix design in frontend/src/components/chat/
- [X] T058 [P] Add loading skeleton for conversation history in frontend/src/components/chat/message-list.tsx

### Edge Cases

- [X] T059 Handle non-task-related messages gracefully (guide user to task management) in backend/app/services/agent.py
- [X] T060 [P] Handle multiple tasks with similar names (ask for clarification) in backend/app/mcp/server.py
- [X] T061 Run quickstart.md manual validation flow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Cleanup (Phase 1)**: No dependencies - can start immediately
- **MCP Server (Phase 2)**: Depends on Phase 1 completion - BLOCKS agent refactor
- **Agent Refactor (Phase 3)**: Depends on Phase 2 (MCP server must be running)
- **User Stories (Phase 4-9)**: All depend on Phase 3 completion (agent using MCP)
  - US1 (Phase 4): First to complete - enables basic chat via MCP
  - US2 (Phase 5): Can start after US1 - requires MCP tool routing
  - US3 (Phase 6): Can start in parallel with US2
  - US4-6 (Phase 7-9): Can start in parallel once US1-3 foundation exists
- **Polish (Phase 10)**: Depends on US1-6 being complete

### MCP Architecture Flow

```
+-------------------------------------------------------------------+
|                        Frontend (Next.js)                         |
|                    ChatKit UI Components                          |
+----------------------+--------------------------------------------+
                       | HTTP
                       v
+-------------------------------------------------------------------+
|                     FastAPI Backend                               |
|  +--------------+    +--------------+    +------------------+     |
|  | Chat Routes  |--->| Agent Service|--->| MCP Client       |     |
|  | /chat        |    | (Gemini AI)  |    | (tool executor)  |     |
|  +--------------+    +--------------+    +--------+---------+     |
|                                                   |               |
|                                          +--------v---------+     |
|                                          | MCP Server       |     |
|                                          | (Official SDK)   |     |
|                                          | - add_task       |     |
|                                          | - list_tasks     |     |
|                                          | - update_task    |     |
|                                          | - complete_toggle|     |
|                                          | - delete_task    |     |
|                                          +--------+---------+     |
|                                                   |               |
|                                          +--------v---------+     |
|                                          |   PostgreSQL     |     |
|                                          |   (Tasks, Chat)  |     |
|                                          +------------------+     |
+-------------------------------------------------------------------+
```

### Parallel Opportunities

- T001-T006 (Cleanup/Setup) - T002, T003, T006 can run in parallel
- T010-T014 (MCP Tools) - All 5 tools can be implemented in parallel
- T030-T032 (Frontend verification) - All can run in parallel
- T052-T055 (Error handling) - T053, T054 can run in parallel
- US4, US5, US6 can run in parallel once US1-3 foundation exists

---

## Parallel Example: MCP Tool Implementation

```bash
# Launch all MCP tool implementations in parallel:
Task T010: "Implement add_task MCP tool"
Task T011: "Implement list_tasks MCP tool"
Task T012: "Implement update_task MCP tool"
Task T013: "Implement complete_task_toggle MCP tool"
Task T014: "Implement delete_task MCP tool"

# After tools complete, integrate with agent:
Task T015-T017: "MCP server integration"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup & Cleanup (T001-T006)
2. Complete Phase 2: MCP Server Implementation (T007-T017)
3. Complete Phase 3: Agent Service Refactor (T018-T026)
4. Complete Phase 4: User Story 1 - Basic Chat (T027-T035)
5. Complete Phase 5: User Story 2 - Add Task (T036-T038)
6. Complete Phase 6: User Story 3 - List Tasks (T039-T041)
7. **STOP and VALIDATE**: Test all P1 stories work independently
8. Deploy MVP

### Incremental Delivery

1. Complete Cleanup + MCP Server + Agent Refactor -> MCP Foundation ready
2. Add User Story 1 -> Test independently -> Deploy (Chat works with MCP!)
3. Add User Story 2 -> Test independently -> Deploy (Can add tasks via MCP!)
4. Add User Story 3 -> Test independently -> Deploy (Can list tasks via MCP!) <- MVP Complete
5. Add User Story 4 -> Test independently -> Deploy (Can toggle completion!)
6. Add User Story 5 -> Test independently -> Deploy (Can update tasks!)
7. Add User Story 6 -> Test independently -> Deploy (Can delete tasks!)
8. Polish phase -> Final validation

---

## Summary

| Phase | Description | Task Count | Key Deliverable |
|-------|-------------|------------|-----------------|
| 1 | Setup & Cleanup | 6 | OpenAI function calling removed |
| 2 | MCP Server Implementation | 11 | Official MCP SDK server with 5 tools |
| 3 | Agent Service Refactor | 9 | Agent uses MCP client for tools |
| 4 | US1 - Chat & Response | 9 | Basic AI chat via MCP |
| 5 | US2 - Add Task | 3 | Create tasks via MCP |
| 6 | US3 - List Tasks | 3 | View tasks via MCP |
| 7 | US4 - Toggle Completion | 4 | Toggle task status via MCP |
| 8 | US5 - Update Task | 3 | Modify tasks via MCP |
| 9 | US6 - Delete Task | 3 | Remove tasks via MCP |
| 10 | Polish | 10 | Error handling, edge cases |
| **Total** | | **61** | |

### Suggested MVP Scope

- **Phase 1-6 (US1-US3)**: 41 tasks
- **Core functionality**: Send/receive messages, add tasks, list tasks - all via MCP SDK
- **Validates**: Full MCP server/client flow, tool execution, conversation persistence

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **MCP SDK**: Using official mcp>=1.0.0 with @mcp.tool() decorators
- **Tools**: add_task, list_tasks, update_task, complete_task_toggle, delete_task
- **Frontend**: ChatKit UI (@chatscope/chat-ui-kit-react) - already implemented
- **Backend**: Gemini 2.0 Flash via OpenAI-compatible endpoint for AI, MCP SDK for tools
