from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from shared.database.connection import get_db
from shared.kafka.producer import get_kafka_producer
from shared.schemas.events import TodoCreatedEvent, TodoUpdatedEvent, TodoDeletedEvent
from shared.utils import generate_uuid
from ..models.todo import Todo, TodoCreate, TodoUpdate
from shared.database.models import Todo as TodoDB

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])


@router.post("/", response_model=Todo)
def create_todo(todo_create: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo item."""
    # Create the database record
    db_todo = TodoDB(
        id=uuid.uuid4(),
        user_id=todo_create.user_id,
        title=todo_create.title,
        description=todo_create.description,
        deadline=todo_create.deadline,
        priority=todo_create.priority,
        status="pending",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    # Convert to response model
    todo_response = Todo(
        id=str(db_todo.id),
        user_id=str(db_todo.user_id),
        title=db_todo.title,
        description=db_todo.description,
        deadline=db_todo.deadline,
        priority=db_todo.priority,
        status=db_todo.status,
        created_at=db_todo.created_at,
        updated_at=db_todo.updated_at
    )

    # Publish event to Kafka
    try:
        kafka_producer = get_kafka_producer()
        event = TodoCreatedEvent(
            todo_id=str(db_todo.id),
            user_id=str(db_todo.user_id),
            title=db_todo.title,
            description=db_todo.description,
            deadline=db_todo.deadline,
            priority=db_todo.priority
        )

        kafka_producer.send_event(
            topic="todo.created",
            key=str(db_todo.user_id),
            value=event.dict()
        )
    except Exception as e:
        # Log the error but don't fail the todo creation
        print(f"Failed to publish todo created event: {str(e)}")

    return todo_response


@router.get("/{todo_id}", response_model=Todo)
def get_todo(todo_id: str, db: Session = Depends(get_db)):
    """Get a specific todo item."""
    db_todo = db.query(TodoDB).filter(TodoDB.id == uuid.UUID(todo_id)).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    return Todo(
        id=str(db_todo.id),
        user_id=str(db_todo.user_id),
        title=db_todo.title,
        description=db_todo.description,
        deadline=db_todo.deadline,
        priority=db_todo.priority,
        status=db_todo.status,
        created_at=db_todo.created_at,
        updated_at=db_todo.updated_at
    )


@router.put("/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    """Update an existing todo item."""
    db_todo = db.query(TodoDB).filter(TodoDB.id == uuid.UUID(todo_id)).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Update fields
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db_todo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_todo)

    # Convert to response model
    todo_response = Todo(
        id=str(db_todo.id),
        user_id=str(db_todo.user_id),
        title=db_todo.title,
        description=db_todo.description,
        deadline=db_todo.deadline,
        priority=db_todo.priority,
        status=db_todo.status,
        created_at=db_todo.created_at,
        updated_at=db_todo.updated_at
    )

    # Publish update event to Kafka
    try:
        kafka_producer = get_kafka_producer()
        event = TodoUpdatedEvent(
            todo_id=str(db_todo.id),
            user_id=str(db_todo.user_id),
            title=db_todo.title,
            description=db_todo.description,
            deadline=db_todo.deadline,
            priority=db_todo.priority
        )

        kafka_producer.send_event(
            topic="todo.updated",
            key=str(db_todo.user_id),
            value=event.dict()
        )
    except Exception as e:
        # Log the error but don't fail the todo update
        print(f"Failed to publish todo updated event: {str(e)}")

    return todo_response


@router.delete("/{todo_id}")
def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    """Delete a todo item."""
    db_todo = db.query(TodoDB).filter(TodoDB.id == uuid.UUID(todo_id)).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Mark as deleted instead of physically deleting
    db_todo.status = "deleted"
    db_todo.updated_at = datetime.utcnow()
    db.commit()

    # Publish delete event to Kafka
    try:
        kafka_producer = get_kafka_producer()
        event = TodoDeletedEvent(
            todo_id=str(db_todo.id),
            user_id=str(db_todo.user_id)
        )

        kafka_producer.send_event(
            topic="todo.deleted",
            key=str(db_todo.user_id),
            value=event.dict()
        )
    except Exception as e:
        # Log the error but don't fail the todo deletion
        print(f"Failed to publish todo deleted event: {str(e)}")

    return {"success": True, "message": "Todo deleted successfully"}