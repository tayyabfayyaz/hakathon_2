# Quickstart Guide: Kafka-based Event-Driven Deadline Notification System

## Prerequisites

- Docker and Docker Compose installed
- Python 3.11+
- Access to Kafka cluster (local or remote)
- PostgreSQL database access

## Local Development Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd kafka-todo-notification-system
```

### 2. Environment Variables
Create a `.env` file in the project root:

```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/todo_app

# Notification Service Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@example.com
SENDER_PASSWORD=your-app-password

TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

### 3. Start Infrastructure
```bash
# Start Kafka, Zookeeper, and PostgreSQL
docker-compose up -d kafka zookeeper postgres
```

### 4. Install Dependencies
```bash
# For Todo Service
cd todo-service
pip install -r requirements.txt

# For Scheduler Service
cd ../scheduler-service
pip install -r requirements.txt

# For Notification Service
cd ../notification-service
pip install -r requirements.txt
```

### 5. Run Services
```bash
# Terminal 1: Start Todo Service
cd todo-service
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Scheduler Service
cd scheduler-service
python app/main.py

# Terminal 3: Start Notification Service
cd notification-service
python app/main.py
```

## Service Endpoints

### Todo Service (Port 8000)
- `POST /api/v1/todos` - Create a new todo with deadline
- `GET /api/v1/todos/{id}` - Get a specific todo
- `PUT /api/v1/todos/{id}` - Update a todo
- `DELETE /api/v1/todos/{id}` - Delete a todo
- `GET /api/v1/users/{user_id}/preferences` - Get user preferences
- `PUT /api/v1/users/{user_id}/preferences` - Update user preferences

## Creating Your First Todo with Deadline

```bash
curl -X POST http://localhost:8000/api/v1/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project proposal",
    "description": "Finish the project proposal document",
    "deadline": "2024-12-31T18:00:00Z",
    "priority": "high",
    "user_id": "user123"
  }'
```

## Testing the Notification System

1. Create a todo with a deadline in the near future (within 15 minutes for reminder)
2. Monitor the Kafka topics for event flow:
   - `todo.created` - Event published when todo is created
   - `deadline.scheduled` - Event published when notification is scheduled
   - `notification.request` - Event published when notification is due
3. Check that notifications are sent according to user preferences

## Configuration Options

### User Preferences
Users can configure notification preferences including:
- Notification channels (email, SMS, push)
- Advance notification timing (1 minute to 7 days)
- Do-not-disturb hours
- Timezone settings

### Environment Variables
- `ADVANCE_NOTIFICATION_MINUTES`: Default minutes before deadline for reminder (default: 15)
- `KAFKA_CONSUMER_GROUP`: Kafka consumer group ID
- `NOTIFICATION_RETRY_ATTEMPTS`: Number of retry attempts for failed notifications (default: 3)
- `HEALTH_CHECK_INTERVAL`: Interval for health checks (default: 30 seconds)

## Troubleshooting

### Common Issues

1. **Kafka Connection Issues**
   - Ensure Kafka and Zookeeper are running
   - Check `KAFKA_BOOTSTRAP_SERVERS` configuration
   - Verify network connectivity

2. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Check `DATABASE_URL` configuration
   - Verify database credentials

3. **Notification Delivery Failures**
   - Check notification service configurations (SMTP, Twilio, etc.)
   - Verify credentials for notification providers
   - Monitor Kafka topics for failed notification events

### Monitoring
- Check service logs for error messages
- Monitor Kafka consumer lag
- Verify database connections and query performance
- Monitor notification delivery rates

## Production Deployment

For production deployment, use the provided Kubernetes manifests and ensure:
- Proper resource allocation for each service
- Secure configuration management for secrets
- Proper backup and disaster recovery procedures
- Monitoring and alerting setup
- Load balancing configuration