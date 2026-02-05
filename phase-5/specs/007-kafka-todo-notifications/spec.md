# Feature Specification: Kafka-based Event-Driven Deadline Notification System

**Feature Branch**: `007-kafka-todo-notifications`
**Created**: 2026-01-31
**Status**: Draft
**Input**: User description: "- We are developing an AI-powered Todo Web Application where users can:

Create and manage todos
Assign deadlines
Receive intelligent reminders
Use AI features for task prioritization
We want to introduce a Kafka-based event-driven deadline notification system that is scalable and microservice-friendly.

#Specification Goals:
Produce a full technical specification including:
- System Overview
- Architecture Design
- Services Definition
- Kafka Event Flow
- Kafka Topic Design
- Event Schemas
- Data Flow Diagram (described in text)
- Service Responsibilities
- Database Interaction Design
- Notification Flow
- Fault Tolerance Strategy
- Scaling Strategy
- Retry & Failure Handling
- Future AI Extension Support

##Required Architecture Components
- Specification must include:
- Todo Service
- Deadline Scheduler Service
- Kafka Broker
- Notification Service
- User Service
- Future AI Automation Service

###Kafka Requirements
Define:
- Topics used
- Event message structure
- Producers and consumers
- Event lifecycle
- Example event flow:
- Todo Created → Deadline Scheduled → Deadline Triggered → Notification Sent

#Functional Requirements
System must:

- Schedule deadline notifications
- Send reminder notifications
- Handle missed deadlines
- Support retries
- Process high event load

#Non-Functional Requirements
System must support:

- Horizontal scalability
- Fault tolerance
- Event durability
- High throughput
- Loose coupling between services

Constraints

- Kafka must be central communication bus.
- Services must remain independently deployable.
- Architecture must support future Kubernetes deployment."

## System Overview

This feature introduces a Kafka-based event-driven deadline notification system for the AI-powered Todo application. The system enables scalable, reliable notifications for todo deadlines while maintaining loose coupling between services.

### Architecture Design

The system follows a microservices architecture with Apache Kafka as the central communication bus. The key components include:

1. **Todo Service**: Handles todo creation, updates, and deletion
2. **Deadline Scheduler Service**: Manages deadline scheduling and triggers
3. **Notification Service**: Processes and delivers notifications to users
4. **User Service**: Manages user preferences and contact information
5. **Kafka Broker**: Central event streaming platform
6. **Future AI Automation Service**: For advanced reminder intelligence

### Kafka Event Flow

The system operates through a series of event-driven interactions:
1. Todo Created → Deadline Scheduled → Deadline Triggered → Notification Sent
2. Events flow asynchronously through Kafka topics
3. Services consume events and perform their designated functions
4. State changes are communicated back through Kafka

### Kafka Topic Design

- `todo.created`: New todo with deadline created
- `todo.updated`: Todo deadline updated
- `todo.deleted`: Todo deleted (cancel scheduled notifications)
- `deadline.scheduled`: Deadline has been scheduled
- `deadline.triggered`: Deadline has been reached
- `notification.request`: Request to send notification
- `notification.sent`: Notification successfully sent
- `notification.failed`: Notification failed

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receive Deadline Reminders (Priority: P1)

As a user, I want to receive timely reminders about upcoming todo deadlines so that I can complete important tasks on time.

**Why this priority**: Critical functionality that delivers core value of the notification system. Without this, the feature doesn't fulfill its primary purpose.

**Independent Test**: Can be fully tested by creating a todo with a deadline and verifying that a notification is sent before the deadline. Delivers immediate value of timely task completion.

**Acceptance Scenarios**:

1. **Given** user creates a todo with a deadline, **When** deadline approaches, **Then** user receives a reminder notification
2. **Given** user has notification preferences set, **When** deadline reminder is due, **Then** notification is sent via preferred channels

---

### User Story 2 - Receive Deadline Reached Notifications (Priority: P1)

As a user, I want to receive notifications when a deadline is reached so that I'm aware of tasks that are now due.

**Why this priority**: Essential for the core notification functionality. Ensures users are aware when tasks become overdue.

**Independent Test**: Can be tested by creating a todo with a past deadline and verifying that a "deadline reached" notification is sent. Provides immediate value of deadline awareness.

**Acceptance Scenarios**:

1. **Given** user has a todo with a deadline, **When** deadline time is reached, **Then** user receives a deadline reached notification
2. **Given** user misses a deadline, **When** deadline passes, **Then** user receives an overdue notification

---

### User Story 3 - Handle Missed Deadlines (Priority: P2)

As a user, I want the system to handle missed deadlines appropriately so that I receive follow-up notifications about overdue tasks.

**Why this priority**: Important for user engagement and task completion, but secondary to initial deadline notifications.

**Independent Test**: Can be tested by allowing a deadline to pass and verifying that overdue notifications are sent according to user preferences.

**Acceptance Scenarios**:

1. **Given** user has missed a deadline, **When** configured follow-up time elapses, **Then** user receives overdue reminder notification

---

### Edge Cases

- What happens when a user deletes a todo before its deadline?
- How does system handle clock synchronization issues across services?
- What occurs when Kafka is temporarily unavailable during event publishing?
- How does the system handle timezone differences for users in different locations?
- What happens when notification delivery fails repeatedly?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST schedule notifications based on todo deadlines and user preferences
- **FR-002**: System MUST send reminder notifications before deadlines (default 15 minutes before)
- **FR-003**: System MUST send deadline reached notifications when deadlines occur
- **FR-004**: System MUST send overdue notifications for missed deadlines
- **FR-005**: System MUST support configurable notification channels (email, SMS, push)
- **FR-006**: System MUST support configurable advance notification timing between 1 minute and 7 days before the deadline
- **FR-007**: System MUST cancel scheduled notifications when todos are deleted
- **FR-008**: System MUST retry failed notifications according to a configurable retry policy
- **FR-009**: System MUST persist notification state to survive service restarts
- **FR-010**: System MUST support user notification preferences (channels, timing, do-not-disturb hours)

### Key Entities *(include if feature involves data)*

- **ScheduledNotification**: Represents a notification scheduled to be sent at a specific time, including todo reference, user reference, scheduled time, and status
- **NotificationRequest**: Contains details for a notification to be sent, including message content, recipient, and delivery channels
- **TodoEvent**: Represents changes to todo items that may trigger notifications, including creation, update, or deletion
- **UserPreferences**: Stores user-specific notification settings including preferred channels, advance notification timing, and do-not-disturb windows

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of deadline notifications are delivered within 1 minute of scheduled time
- **SC-002**: System supports 10,000 concurrent scheduled notifications without performance degradation
- **SC-003**: 90% of users acknowledge receiving deadline reminders as helpful
- **SC-004**: System maintains 99.9% uptime for notification delivery
- **SC-005**: Notification delivery success rate is above 98%
- **SC-006**: System can process 1,000 todo creation events per minute without delay
- **SC-007**: Failed notifications are retried successfully in 85% of cases