# TODO CLI

A lightweight, interactive command-line task manager built with Python.

## Overview

TODO CLI provides a simple menu-driven interface for managing your tasks directly from the terminal. It features in-memory storage for quick, session-based task management.

## Features

- **Interactive menu interface** - Navigate with simple number selections
- **Add tasks** - Create new to-do items with descriptions
- **List tasks** - View all tasks with status indicators
- **Update tasks** - Modify task descriptions
- **Toggle status** - Switch tasks between Remaining and Completed
- **Delete tasks** - Remove tasks you no longer need

## Requirements

- Python 3.10 or higher

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/todo-cli.git
cd todo-cli

# Install dependencies
pip install -r requirements.txt
```

## Usage

Start the interactive application:

```bash
python -m src.main
```

Or if installed as a package:

```bash
todo-cli
```

### Menu Options

```
==================================================
          TODO CLI - Task Manager
          (In-Memory Storage)
==================================================

Please select an option:

  1. List Tasks
  2. Add Task
  3. Update Task
  4. Toggle Task Status
  5. Delete Task
  6. Exit
```

### Example Session

```
Enter your choice (1-6): 2

--------------------------------------------------
               ADD NEW TASK
--------------------------------------------------

Enter task description: Buy groceries

Success! Task 'Buy groceries' added with ID 1.
Press Enter to continue...
```

## Project Structure

```
todo-cli/
├── src/
│   ├── __init__.py
│   ├── main.py        # CLI entry point and menu logic
│   ├── models.py      # TodoItem data model (Pydantic)
│   └── database.py    # In-memory storage handler
├── tests/
│   └── test_main.py   # Test suite
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Running Tests

```bash
pytest tests/ -v
```

## Technical Details

- **Data validation**: Pydantic v2
- **Storage**: In-memory (data persists only during session)
- **Python**: 3.10+

## License

MIT License
