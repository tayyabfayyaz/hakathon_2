"""Notification CRUD endpoints."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from sqlmodel import select, func

from app.api.deps import CurrentUserDep, SessionDep
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
    MarkAsReadRequest,
    MarkAsReadResponse,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Status constants
STATUS_READ = "read"
STATUS_DISMISSED = "dismissed"


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    current_user: CurrentUserDep,
    session: SessionDep,
    unread_only: bool = Query(False, description="Filter to show only unread notifications"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
) -> dict:
    """
    List notifications for the authenticated user.

    - **unread_only**: If true, only return unread notifications
    - **limit**: Maximum number of notifications to return (default: 50, max: 100)
    - **offset**: Number of notifications to skip for pagination

    Returns notifications sorted by creation date (newest first).
    """
    # Build base query
    statement = select(Notification).where(Notification.user_id == current_user.id)

    if unread_only:
        statement = statement.where(Notification.status != STATUS_READ)

    # Get total count before pagination
    count_statement = select(func.count()).select_from(
        statement.subquery()
    )
    count_result = await session.exec(count_statement)
    total_count = count_result.one()

    # Get unread count
    unread_statement = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.status != STATUS_READ,
        Notification.status != STATUS_DISMISSED,
    )
    unread_result = await session.exec(unread_statement)
    unread_count = unread_result.one()

    # Apply pagination and ordering
    statement = statement.order_by(Notification.created_at.desc()).offset(offset).limit(limit)

    result = await session.exec(statement)
    notifications = result.all()

    return {
        "notifications": notifications,
        "count": total_count,
        "unread_count": unread_count,
    }


@router.get("/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict:
    """
    Get the count of unread notifications for the authenticated user.
    """
    statement = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.status != STATUS_READ,
        Notification.status != STATUS_DISMISSED,
    )
    result = await session.exec(statement)
    unread_count = result.one()

    return {"unread_count": unread_count}


@router.post("/mark-read", response_model=MarkAsReadResponse)
async def mark_notifications_as_read(
    request: MarkAsReadRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict:
    """
    Mark specific notifications as read.

    - **notification_ids**: List of notification IDs to mark as read
    """
    now = datetime.utcnow()
    marked_count = 0

    for notification_id in request.notification_ids:
        statement = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        result = await session.exec(statement)
        notification = result.first()

        if notification and notification.status != STATUS_READ:
            notification.status = STATUS_READ
            notification.read_at = now
            session.add(notification)
            marked_count += 1

    await session.commit()

    return {
        "marked_count": marked_count,
        "message": f"Marked {marked_count} notification(s) as read",
    }


@router.post("/mark-all-read", response_model=MarkAsReadResponse)
async def mark_all_as_read(
    current_user: CurrentUserDep,
    session: SessionDep,
) -> dict:
    """
    Mark all notifications as read for the authenticated user.
    """
    now = datetime.utcnow()

    # Get all unread notifications
    statement = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.status != STATUS_READ,
        Notification.status != STATUS_DISMISSED,
    )
    result = await session.exec(statement)
    notifications = result.all()

    marked_count = 0
    for notification in notifications:
        notification.status = STATUS_READ
        notification.read_at = now
        session.add(notification)
        marked_count += 1

    await session.commit()

    return {
        "marked_count": marked_count,
        "message": f"Marked {marked_count} notification(s) as read",
    }


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def dismiss_notification(
    notification_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
) -> None:
    """
    Dismiss (delete) a notification.

    Returns 404 if notification doesn't exist or belongs to another user.
    """
    statement = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    )
    result = await session.exec(statement)
    notification = result.first()

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    await session.delete(notification)
    await session.commit()
