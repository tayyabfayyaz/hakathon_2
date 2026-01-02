"""TODO CLI - An interactive in-memory to-do list application.

This module provides an interactive menu-driven CLI for managing to-do items.
All data is stored in memory and will be lost when the application exits.

Usage:
    todo-cli    # Start the interactive menu
"""

import sys

from src.database import storage
from src.models import TodoItem


def clear_screen():
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")


def print_header():
    """Print the application header."""
    print("=" * 50)
    print("          TODO CLI - Task Manager")
    print("          (In-Memory Storage)")
    print("=" * 50)
    print()


def print_menu():
    """Print the main menu options."""
    print("Please select an option:")
    print()
    print("  1. List Tasks")
    print("  2. Add Task")
    print("  3. Update Task")
    print("  4. Toggle Task Status")
    print("  5. Delete Task")
    print("  6. Exit")
    print()


def list_tasks():
    """Display all tasks in a formatted table."""
    todos = storage.get_all()
    print()
    print("-" * 50)
    print("               TASK LIST")
    print("-" * 50)

    if not todos:
        print("  No tasks yet. Add your first task!")
    else:
        print(f"  {'ID':<4} | {'Description':<25} | {'Status':<10}")
        print("  " + "-" * 46)
        for todo in todos:
            status_icon = "[x]" if todo.status == "Completed" else "[ ]"
            print(f"  {todo.id:<4} | {todo.description[:25]:<25} | {status_icon} {todo.status}")

    print("-" * 50)
    print()
    input("Press Enter to continue...")


def add_task():
    """Add a new task interactively."""
    print()
    print("-" * 50)
    print("               ADD NEW TASK")
    print("-" * 50)
    print()

    description = input("Enter task description: ").strip()

    if not description:
        print("\nError: Description cannot be empty.")
        input("Press Enter to continue...")
        return

    new_id = storage.get_next_id()
    new_todo = TodoItem(id=new_id, description=description)
    storage.add(new_todo)

    print(f"\nSuccess! Task '{description}' added with ID {new_id}.")
    input("Press Enter to continue...")


def update_task():
    """Update an existing task's description."""
    print()
    print("-" * 50)
    print("               UPDATE TASK")
    print("-" * 50)

    todos = storage.get_all()
    if not todos:
        print("\nNo tasks to update.")
        input("Press Enter to continue...")
        return

    print("\nCurrent tasks:")
    for todo in todos:
        print(f"  {todo.id}: {todo.description}")
    print()

    try:
        task_id = int(input("Enter task ID to update: "))
    except ValueError:
        print("\nError: Please enter a valid number.")
        input("Press Enter to continue...")
        return

    if not storage.find_by_id(task_id):
        print(f"\nError: Task with ID {task_id} not found.")
        input("Press Enter to continue...")
        return

    new_description = input("Enter new description: ").strip()

    if not new_description:
        print("\nError: Description cannot be empty.")
        input("Press Enter to continue...")
        return

    storage.update(task_id, new_description)
    print(f"\nSuccess! Task {task_id} has been updated.")
    input("Press Enter to continue...")


def toggle_status():
    """Toggle a task's status between Remaining and Completed."""
    print()
    print("-" * 50)
    print("            TOGGLE TASK STATUS")
    print("-" * 50)

    todos = storage.get_all()
    if not todos:
        print("\nNo tasks to toggle.")
        input("Press Enter to continue...")
        return

    print("\nCurrent tasks:")
    for todo in todos:
        status_icon = "[x]" if todo.status == "Completed" else "[ ]"
        print(f"  {todo.id}: {status_icon} {todo.description}")
    print()

    try:
        task_id = int(input("Enter task ID to toggle: "))
    except ValueError:
        print("\nError: Please enter a valid number.")
        input("Press Enter to continue...")
        return

    todo = storage.toggle(task_id)
    if todo:
        print(f"\nSuccess! Task {task_id} is now '{todo.status}'.")
    else:
        print(f"\nError: Task with ID {task_id} not found.")

    input("Press Enter to continue...")


def delete_task():
    """Delete a task by its ID."""
    print()
    print("-" * 50)
    print("               DELETE TASK")
    print("-" * 50)

    todos = storage.get_all()
    if not todos:
        print("\nNo tasks to delete.")
        input("Press Enter to continue...")
        return

    print("\nCurrent tasks:")
    for todo in todos:
        print(f"  {todo.id}: {todo.description}")
    print()

    try:
        task_id = int(input("Enter task ID to delete: "))
    except ValueError:
        print("\nError: Please enter a valid number.")
        input("Press Enter to continue...")
        return

    if storage.delete(task_id):
        print(f"\nSuccess! Task {task_id} has been deleted.")
    else:
        print(f"\nError: Task with ID {task_id} not found.")

    input("Press Enter to continue...")


def main():
    """Main entry point for the interactive CLI."""
    while True:
        clear_screen()
        print_header()
        print_menu()

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            list_tasks()
        elif choice == "2":
            add_task()
        elif choice == "3":
            update_task()
        elif choice == "4":
            toggle_status()
        elif choice == "5":
            delete_task()
        elif choice == "6":
            clear_screen()
            print("Thank you for using TODO CLI!")
            print("Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter 1-6.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
