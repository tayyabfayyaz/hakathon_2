# TodoList Pro - Kafka Notification System Integration

This project integrates a Kafka-based event-driven deadline notification system with the TodoList Pro frontend and backend applications.

## Architecture Overview

The system consists of:
- **Frontend**: Next.js application for task management with deadline functionality
- **Backend**: FastAPI application with task CRUD operations and Kafka integration
- **Notification Services**: Independent services that handle deadline notifications via Kafka events
- **Kafka**: Message broker for event-driven communication between services

## How It Works

1. **Task Creation**: When a user creates a task with a deadline in the frontend:
   - Frontend sends request to Backend API
   - Backend creates the task in the database
   - Backend publishes a `todo.created` event to Kafka
   - Notification Scheduler service receives the event and schedules notifications

2. **Task Updates**: When a user updates a task deadline:
   - Frontend sends request to Backend API
   - Backend updates the task in the database
   - Backend publishes a `todo.updated` event to Kafka
   - Notification Scheduler service receives the event and updates/cancels scheduled notifications

3. **Task Deletion**: When a user deletes a task:
   - Frontend sends request to Backend API
   - Backend deletes the task from the database
   - Backend publishes a `todo.deleted` event to Kafka
   - Notification Scheduler service receives the event and cancels scheduled notifications

## Kafka Events

The system uses the following Kafka topics:
- `todo.created` - Published when a new task is created
- `todo.updated` - Published when a task is updated
- `todo.deleted` - Published when a task is deleted

## Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Kafka and Zookeeper
- PostgreSQL

## Setup Instructions

### 1. Backend Setup

```bash
cd backend/hf-deploy
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

Configure environment variables in `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost/dbname
BETTER_AUTH_SECRET=your-secret-key
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_ENABLED=true
```

Run the backend:
```bash
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Configure environment variables in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Kafka Setup

Start Kafka and Zookeeper:
```bash
# Start ZooKeeper
zookeeper-server-start /path/to/zookeeper.properties

# Start Kafka
kafka-server-start /path/to/server.properties

# Create required topics
kafka-topics --create --topic todo.created --bootstrap-server localhost:9092
kafka-topics --create --topic todo.updated --bootstrap-server localhost:9092
kafka-topics --create --topic todo.deleted --bootstrap-server localhost:9092
kafka-topics --create --topic notification.request --bootstrap-server localhost:9092
kafka-topics --create --topic notification.sent --bootstrap-server localhost:9092
kafka-topics --create --topic notification.failed --bootstrap-server localhost:9092
```

### 4. Notification Services Setup

The notification services are located in the `kafka-todo-notification-system` directory:

```bash
cd kafka-todo-notification-system
```

Run the individual services:

**Scheduler Service** (handles scheduling of notifications):
```bash
cd scheduler-service
python -m app.main
```

**Notification Service** (handles sending notifications):
```bash
cd notification-service
python -m app.main
```

## Usage

1. Access the frontend at `http://localhost:3000`
2. Create an account or sign in
3. Create tasks with deadlines using the calendar icon
4. The notification system will automatically schedule and send reminders based on the deadlines

## Features

- **Deadline Reminders**: Automatic notifications sent before deadlines
- **Deadline Reached Notifications**: Notifications when deadlines are reached
- **Missed Deadline Handling**: Follow-up notifications for overdue tasks
- **Multi-channel Delivery**: Support for email, SMS, and push notifications
- **Retry Mechanism**: Failed notifications are retried with exponential backoff
- **Dead Letter Queue**: Permanently failed notifications are logged for manual processing
- **Do-Not-Disturb Hours**: Respect user preferences for quiet hours
- **Configurable Timing**: Adjustable notification timing (1 minute to 7 days before deadline)

## Monitoring and Troubleshooting

- Check Kafka topic messages: `kafka-console-consumer --topic todo.created --from-beginning --bootstrap-server localhost:9092`
- Monitor backend logs for Kafka connection status
- Check notification service logs for processing status
- Use the dead letter queue to handle permanently failed notifications

## Scaling

The system is designed to be horizontally scalable:
- Multiple instances of the backend can run behind a load balancer
- Multiple instances of notification services can consume from Kafka topics
- Kafka partitions allow for parallel processing
- Database connections are pooled for efficiency