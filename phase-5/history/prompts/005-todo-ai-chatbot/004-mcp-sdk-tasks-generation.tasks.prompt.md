---
id: 004
title: MCP SDK Tasks Generation
stage: tasks
date: 2026-01-09
surface: agent
model: claude-opus-4-5-20251101
feature: 005-todo-ai-chatbot
branch: main
user: user
command: /sp.tasks
labels: ["mcp-sdk", "tasks", "refactor", "official-mcp"]
links:
  spec: specs/005-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/005-todo-ai-chatbot/tasks.md
tests:
  - null
---

## Prompt

- In the 005 spec folder you edit the tasks.md file and add some new tasks.
- Remove the mcp OpenAI function calling.
- Build MCP server with the Official MCP SDK to operate the todo tool by the chatbot.
- Tasks: add_task, update_task, list_task, complete_task_toggle, delete_task
- Use ChatKit_UI for the frontend of chatbot.

## Response snapshot

Generated new tasks.md file for 005-todo-ai-chatbot feature with 61 tasks across 10 phases:

**Key Changes:**
1. Phase 1: Setup & Cleanup - Remove OpenAI function calling (T001-T006)
2. Phase 2: MCP Server Implementation with Official SDK (T007-T017)
3. Phase 3: Agent Service Refactor with MCP Client (T018-T026)
4. Phases 4-9: User Stories 1-6 implementation via MCP
5. Phase 10: Polish & Cross-Cutting Concerns

**MCP Tools Implemented:**
- add_task - Create new tasks
- list_tasks - View user tasks
- update_task - Modify task details
- complete_task_toggle - Toggle completion status
- delete_task - Remove tasks

**Architecture:**
Frontend (ChatKit UI) -> FastAPI -> Agent Service -> MCP Client -> MCP Server (Official SDK) -> PostgreSQL

## Outcome

- Impact: Generated comprehensive task list for migrating from OpenAI function calling to Official MCP SDK
- Tests: No tests added (verification tasks included)
- Files: specs/005-todo-ai-chatbot/tasks.md (created/updated)
- Next prompts: /sp.implement to execute the tasks
- Reflection: Successfully restructured tasks to use MCP SDK with proper tool decorators instead of OpenAI function calling format

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Execute Phase 1 cleanup tasks
