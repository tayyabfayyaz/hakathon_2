---
id: 006
title: Agent Behavior Intent Detection Update
stage: refactor
date: 2026-01-10
surface: agent
model: claude-opus-4-5-20251101
feature: 005-todo-ai-chatbot
branch: main
user: developer
command: /sp.implement
labels: ["agent", "intent-detection", "tool-routing", "refactor"]
links:
  spec: specs/005-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/services/agent.py (modified)
tests:
  - Backend server auto-reload confirmed
---

## Prompt

Update the agent behavior:
- Task Creation: When user mentions adding/creating/remembering something, use add_task
- Task Listing: When user asks to see/show/list tasks, use list_tasks with appropriate filter
- Task Completion: When user says done/complete/finished, use complete_task
- Task Deletion: When user says delete/remove/cancel, use delete_task
- Task Update: When user says change/update/rename, use update_task
- Confirmation: Always confirm actions with friendly response
- Error Handling: Gracefully handle task not found and other errors

## Response snapshot

Updated the AgentService with improved intent detection and tool routing:

**Enhanced Keywords:**
- ADD: add, create, remember, remind, need to, have to, should, must, todo, want to, gotta, gonna, plan to
- LIST: list, show, see, view, display, what are, my tasks, all tasks, pending
- COMPLETE: done, complete, finish, finished, completed, mark, check, tick, accomplish
- DELETE: delete, remove, cancel, get rid, drop, trash, eliminate, clear, erase
- UPDATE: update, change, edit, modify, rename, fix, correct, alter, revise

**New Features:**
- Priority-based intent detection (delete > complete > update > list > add)
- Task verb detection (buy, call, email, etc.) for implicit task creation
- Greeting filtering to avoid tool execution on casual messages
- `_format_friendly_response()` method for consistent confirmations
- Graceful error handling with clarification prompts for:
  - Task not found
  - Multiple matching tasks
  - General errors

**Tool Routing:**
- add -> add_task
- list -> list_tasks
- complete -> complete_task_toggle
- delete -> delete_task
- update -> update_task

## Outcome

- Impact: Improved NL understanding and friendlier responses
- Tests: Backend auto-reload confirmed
- Files: 1 file modified (backend/app/services/agent.py)
- Next prompts: Test various NL inputs in chat UI
- Reflection: Priority order prevents ambiguous keyword conflicts

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Server reload PASS
- Prompt variant (if applicable): N/A
- Next experiment: Add more task verbs for implicit creation detection
