# TODO CLI

A simple and easy-to-use command-line to-do list application built with Python.

Manage your tasks directly from the terminal - add tasks, mark them complete, update descriptions, and more!

---

## Features

- **Add tasks** - Create new to-do items with descriptions
- **List tasks** - View all your tasks with their status
- **Update tasks** - Change the description of existing tasks
- **Toggle status** - Mark tasks as Completed or Remaining
- **Delete tasks** - Remove tasks you no longer need
- **Persistent storage** - Your tasks are saved automatically to a JSON file

---

## Prerequisites

Before you begin, make sure you have:

- **Python 3.10 or higher** installed on your system
- **pip** (Python package manager)

To check your Python version:

```bash
python --version
```

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/todo_cli.git
cd todo_cli
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `typer` - For building the CLI interface
- `pydantic` - For data validation
- `pytest` - For running tests

---

## Quick Start

Here's how to get started in 30 seconds:

```bash
# Add your first task
python -m src.main add "Learn Python"

# See your tasks
python -m src.main list

# Mark it as complete
python -m src.main toggle 1

# View updated list
python -m src.main list
```

---

## Command Reference

### 1. Add a Task

Create a new to-do item.

```bash
python -m src.main add "Your task description"
```

**Example:**

```bash
python -m src.main add "Buy groceries"
```

**Output:**

```
Task 'Buy groceries' has been added.
```

---

### 2. List All Tasks

View all your to-do items with their ID, description, and status.

```bash
python -m src.main list
```

**Output:**

```
ID | Description | Status
-- | --- | ---
1 | Buy groceries | Remaining
2 | Finish homework | Remaining
3 | Call mom | Completed
```

If you have no tasks, you'll see:

```
No to-do items yet.
```

---

### 3. Update a Task

Change the description of an existing task.

```bash
python -m src.main update <task_id> "New description"
```

**Example:**

```bash
python -m src.main update 1 "Buy organic groceries"
```

**Output:**

```
Task 1 has been updated.
```

---

### 4. Toggle Task Status

Switch a task between "Remaining" and "Completed".

```bash
python -m src.main toggle <task_id>
```

**Example:**

```bash
python -m src.main toggle 1
```

**Output:**

```
Task 1 status changed to 'Completed'.
```

Run the same command again to change it back to "Remaining".

---

### 5. Delete a Task

Remove a task permanently.

```bash
python -m src.main delete <task_id>
```

**Example:**

```bash
python -m src.main delete 1
```

**Output:**

```
Task 1 has been deleted.
```

---

### 6. Get Help

View all available commands and options.

```bash
python -m src.main --help
```

Get help for a specific command:

```bash
python -m src.main add --help
```

---

## Example Workflow

Here's a typical workflow for managing your daily tasks:

```bash
# Morning: Add today's tasks
python -m src.main add "Reply to emails"
python -m src.main add "Attend team meeting"
python -m src.main add "Review pull requests"
python -m src.main add "Write documentation"

# Check your task list
python -m src.main list

# Output:
# ID | Description | Status
# -- | --- | ---
# 1 | Reply to emails | Remaining
# 2 | Attend team meeting | Remaining
# 3 | Review pull requests | Remaining
# 4 | Write documentation | Remaining

# Complete a task
python -m src.main toggle 1

# Update a task description
python -m src.main update 2 "Attend team meeting at 3 PM"

# End of day: Check progress
python -m src.main list

# Remove a cancelled task
python -m src.main delete 4
```

---

## Project Structure

```
todo_cli/
├── src/
│   ├── main.py          # CLI commands and entry point
│   ├── models.py        # Data models (TodoItem)
│   └── database.py      # JSON file storage
├── tests/
│   └── test_main.py     # Test suite
├── requirements.txt     # Project dependencies
├── pytest.ini           # Pytest configuration
├── todo_database.json   # Your tasks (created automatically)
└── README.md            # This file
```

---

## Data Storage

Your tasks are automatically saved to `todo_database.json` in the project folder.

**Example file content:**

```json
[
    {
        "id": 1,
        "description": "Buy groceries",
        "status": "Remaining"
    },
    {
        "id": 2,
        "description": "Call mom",
        "status": "Completed"
    }
]
```

- The file is created automatically when you add your first task
- All changes are saved immediately
- You can backup this file to preserve your tasks

---

## Running Tests

Run the test suite to verify everything works correctly:

```bash
pytest tests/test_main.py -v
```

Run all tests with coverage:

```bash
pytest -v
```

---

## Troubleshooting

### "Command not found" or "Module not found"

Make sure you're in the project root directory:

```bash
cd path/to/todo_cli
```

### "Task with ID X not found"

The task ID doesn't exist. Use `python -m src.main list` to see available task IDs.

### Dependencies not installed

Run the installation command again:

```bash
pip install -r requirements.txt
```

---

## Built With

- [Python](https://www.python.org/) - Programming language
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation

---

## License

This project is open source and available under the MIT License.
