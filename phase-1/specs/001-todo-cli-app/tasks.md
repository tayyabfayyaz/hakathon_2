# Tasks: CLI To-Do List

**Input**: Design documents from `D:\hakathon_2\todo_cli\specs\001-todo-cli-app\`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md

**Tests**: The constitution mandates a Test-First approach. Test tasks are included for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure as defined in `plan.md` (`src`, `tests`)
- [X] T002 Create `requirements.txt` file in the root directory
- [X] T003 [P] Add `typer` and `pydantic` to `requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [X] T004 Implement the Pydantic model for `TodoItem` in `src/models.py` based on `data-model.md`
- [X] T005 Implement the database module in `src/database.py` to handle reading and writing to the JSON data file. This module should include functions for initializing the database, getting all todos, and saving all todos. It must handle file creation if the JSON file doesn't exist and ensure atomic writes.

---

## Phase 3: User Story 1 & 2 - Add and List Tasks (Priority: P1)

**Goal**: Allow users to add a new task and see the list of all tasks. These are grouped together as listing is required to verify adding.

**Independent Test**: User can run `todo add "New Task"` and then `todo list` to see the new task in the output.

### Tests for User Story 1 & 2

- [X] T006 [P] [US1] In `tests/test_main.py`, write a test for adding a new task that verifies the task is correctly added to the database.
- [X] T007 [P] [US2] In `tests/test_main.py`, write a test for listing tasks that verifies all tasks are displayed correctly.
- [X] T008 [P] [US2] In `tests/test_main.py`, write a test for listing tasks when the database is empty, ensuring a proper message is shown.

### Implementation for User Story 1 & 2

- [X] T009 [US1] Implement the `add` command in `src/main.py` using Typer. This command should take a description, create a `TodoItem`, and save it to the database.
- [X] T010 [US2] Implement the `list` command in `src/main.py` using Typer. This command should retrieve all tasks from the database and display them in a formatted table.

---

## Phase 4: User Story 3 - Update a Task (Priority: P2)

**Goal**: Allow users to update the description of an existing task.

**Independent Test**: User can run `todo update 1 "New Description"` and then `todo list` to see the updated task.

### Tests for User Story 3

- [X] T011 [P] [US3] In `tests/test_main.py`, write a test for updating a task's description.
- [X] T012 [P] [US3] In `tests/test_main.py`, write a test for updating a non-existent task to ensure an error is handled correctly.

### Implementation for User Story 3

- [X] T013 [US3] Implement the `update` command in `src/main.py`. This command should take a task ID and a new description, update the corresponding task in the database.

---

## Phase 5: User Story 4 - Toggle Task Status (Priority: P2)

**Goal**: Allow users to toggle a task's status between "Remaining" and "Completed".

**Independent Test**: User can run `todo toggle 1` and then `todo list` to see the updated status.

### Tests for User Story 4

- [X] T014 [P] [US4] In `tests/test_main.py`, write a test for toggling a task's status from "Remaining" to "Completed".
- [X] T015 [P] [US4] In `tests/test_main.py`, write a test for toggling a task's status from "Completed" to "Remaining".
- [X] T016 [P] [US4] In `tests/test_main.py`, write a test for toggling a non-existent task to ensure an error is handled correctly.

### Implementation for User Story 4

- [X] T017 [US4] Implement the `toggle` command in `src/main.py`. This command should take a task ID and toggle its status in the database.

---

## Phase 6: User Story 5 - Delete a Task (Priority: P3)

**Goal**: Allow users to delete a task from the list.

**Independent Test**: User can run `todo delete 1` and then `todo list` to verify the task has been removed.

### Tests for User Story 5

- [X] T018 [P] [US5] In `tests/test_main.py`, write a test for deleting a task.
- [X] T019 [P] [US5] In `tests/test_main.py`, write a test for deleting a non-existent task to ensure an error is handled correctly.

### Implementation for User Story 5

- [X] T020 [US5] Implement the `delete` command in `src/main.py`. This command should take a task ID and remove the corresponding task from the database.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories.

- [X] T021 [P] Implement robust error handling for all commands for cases like invalid file permissions or corrupted JSON.
- [X] T022 [P] Refine the command-line output for clarity and better user experience.
- [X] T023 [P] Add docstrings to all functions and modules.
- [X] T024 [P] Update `README.md` with final usage instructions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup.
- **User Stories (Phase 3+)**: Depend on Foundational. User stories can be implemented in priority order, but US1 & US2 are best done together.
- **Polish (Phase 7)**: Depends on all user stories being complete.

### User Story Dependencies

- **US1 & US2**: Should be implemented together as a baseline.
- **US3, US4, US5**: Can be implemented in any order after US1 & US2 are complete.

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1.  Complete Phase 1: Setup
2.  Complete Phase 2: Foundational
3.  Complete Phase 3: User Story 1 & 2
4.  **STOP and VALIDATE**: The core functionality of adding and listing tasks should work.

### Incremental Delivery

1.  Deliver MVP (Add/List).
2.  Add User Story 3 (Update).
3.  Add User Story 4 (Toggle).
4.  Add User Story 5 (Delete).
5.  Complete Polish phase.
