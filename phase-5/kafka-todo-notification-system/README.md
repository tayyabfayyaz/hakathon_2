# AI Todo App – Kafka-based Deadline Notification System

This is a microservices-based todo application with a Kafka-powered deadline notification system. The system enables real-time notifications, scalable event processing, and future AI workflow automation.

## Architecture Overview

The system consists of three main services:

1. **Todo Service**: Handles CRUD operations for todo items
2. **Scheduler Service**: Manages deadline notifications and scheduling
3. **Notification Service**: Sends notifications to users via various channels

Communication between services happens through Apache Kafka topics.

## Kafka Topics

- `todo.created` - New todo with deadline created
- `todo.updated` - Todo deadline updated
- `todo.deleted` - Todo deleted (cancel scheduled notifications)
- `deadline.scheduled` - Deadline has been scheduled
- `deadline.triggered` - Deadline has been reached
- `notification.request` - Request to send notification
- `notification.sent` - Notification successfully sent
- `notification.failed` - Notification failed

## Prerequisites

- Docker
- Docker Compose
- Python 3.11+

## Running the System

1. Clone the repository
2. Navigate to the project directory
3. Start the services:

```bash
docker-compose up --build
```

This will start:
- Kafka and Zookeeper
- PostgreSQL database
- Todo Service (available at http://localhost:8000)
- Scheduler Service
- Notification Service

## API Usage

### Create a Todo with Deadline

```bash
curl -X POST http://localhost:8000/api/v1/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the Kafka notification system",
    "deadline": "2024-12-31T23:59:59Z",
    "priority": "high",
    "user_id": "user123"
  }'
```

### Update a Todo

```bash
curl -X PUT http://localhost:8000/api/v1/todos/{todo_id} \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated project title",
    "deadline": "2024-12-31T23:59:59Z",
    "priority": "normal"
  }'
```

### Delete a Todo

```bash
curl -X DELETE http://localhost:8000/api/v1/todos/{todo_id}
```

## System Features

- Real-time notifications via Kafka
- Configurable advance notifications (default 15 minutes before deadline)
- Support for multiple notification channels (email, SMS, push)
- Scalable architecture with microservices
- Fault tolerance with retry mechanisms
- Horizontal scaling capability

## Event Flow

1. User creates todo with deadline
2. Todo Service publishes `todo.created` event to Kafka
3. Scheduler Service consumes event and schedules notifications
4. At reminder time, Scheduler publishes `notification.request` event
5. Notification Service consumes event and sends notification
6. Notification Service publishes `notification.sent` or `notification.failed` event

## Configuration

Environment variables can be set in the docker-compose.yml file:

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `DATABASE_URL`: PostgreSQL connection string
- `ADVANCE_NOTIFICATION_MINUTES`: Minutes before deadline to send reminder

## Testing

Unit and integration tests are defined in the testing_plan.md file. To run tests in a development environment:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests using pytest:
```bash
pytest tests/
```

## Future Extensions

- AI task prioritization
- Smart reminder prediction
- Multi-device notifications
- Advanced scheduling options
- User preference management UI

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License