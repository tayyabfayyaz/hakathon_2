# Implementation Plan: Kafka-based Event-Driven Deadline Notification System

## Technical Context

This implementation plan covers the development of a Kafka-based event-driven deadline notification system for the AI-powered Todo application. The system will consist of multiple microservices communicating through Apache Kafka to provide scalable, reliable notifications for todo deadlines.

**Feature**: Kafka-based Event-Driven Deadline Notification System
**Branch**: 007-kafka-todo-notifications
**Target Architecture**: Microservices with Kafka as central event bus

### Technology Stack

- **Backend Services**: Python (FastAPI for web services, standalone Python for schedulers)
- **Message Queue**: Apache Kafka
- **Database**: PostgreSQL (for persistence)
- **Scheduling**: APScheduler (Advanced Python Scheduler)
- **Containerization**: Docker & Docker Compose
- **Orchestration**: Kubernetes-ready configuration

### System Components

1. **Todo Service**: REST API for todo management with Kafka producer
2. **Scheduler Service**: Background service for managing deadline notifications
3. **Notification Service**: Service for delivering notifications via multiple channels
4. **User Service**: Management of user preferences and contact information
5. **Kafka Infrastructure**: Event streaming platform

## Constitution Check

### Quality Standards
- All services follow microservice principles with single responsibility
- Kafka is used as the central communication bus between services
- Services remain independently deployable
- All external dependencies are documented
- Error handling and retry mechanisms are implemented

### Performance & Reliability
- System supports horizontal scalability
- Event durability is ensured through Kafka configuration
- Services are fault-tolerant with proper error handling
- High throughput is maintained through asynchronous processing

### Security
- Services communicate securely through Kafka
- User data is protected and privacy-compliant
- Authentication and authorization patterns are followed

## Phase 0: Research & Resolution of Unknowns

### Research Tasks

1. **Kafka Integration Patterns**
   - Best practices for Python Kafka integration
   - Producer and consumer configuration for reliability
   - Error handling and retry strategies
   - Partitioning strategies for scalability

2. **Scheduler Implementation**
   - Comparison of different Python scheduling libraries
   - Persistence of scheduled jobs across restarts
   - Timezone handling for global users
   - Clock synchronization strategies

3. **Notification Channel Selection**
   - Email service providers (SMTP configuration)
   - SMS service providers (Twilio, AWS SNS, etc.)
   - Push notification services (Firebase, APNs)
   - Rate limiting and cost considerations

4. **Database Design**
   - Optimal schema design for scheduled notifications
   - Indexing strategies for efficient querying
   - Transaction handling for consistency
   - Migration strategies for schema evolution

### Decision Summary

- **Kafka Client**: kafka-python for Python integration
- **Scheduler**: APScheduler with persistent job stores
- **Notification Channels**: Email (SMTP), SMS (Twilio API), Push (Firebase Cloud Messaging)
- **Database**: PostgreSQL with SQLAlchemy ORM

## Phase 1: Data Model & API Contracts

### Data Model (data-model.md)

#### ScheduledNotification Entity
- **Fields**:
  - id: UUID (primary key)
  - todo_id: UUID (foreign key to todo)
  - user_id: UUID (foreign key to user)
  - scheduled_time: DateTime (when notification should be sent)
  - notification_type: String (reminder|deadline|overdue)
  - status: String (pending|triggered|sent|failed)
  - created_at: DateTime
  - processed_at: DateTime (nullable)
- **Relationships**: Links to Todo and User entities
- **Indexes**: On scheduled_time, todo_id, user_id for efficient querying

#### NotificationRequest Entity
- **Fields**:
  - id: UUID (primary key)
  - todo_id: UUID (foreign key to todo)
  - user_id: UUID (foreign key to user)
  - title: String (todo title)
  - message: String (notification message)
  - deadline: DateTime (original deadline)
  - channels: JSON (list of notification channels)
  - priority: String (low|normal|high)
  - status: String (pending|processing|sent|failed)
  - created_at: DateTime
  - sent_at: DateTime (nullable)
- **Relationships**: Links to Todo and User entities

#### TodoEvent Entity
- **Fields**:
  - id: UUID (primary key)
  - todo_id: UUID (foreign key to todo)
  - user_id: UUID (foreign key to user)
  - event_type: String (created|updated|deleted)
  - payload: JSON (event data)
  - created_at: DateTime
- **Purpose**: Track todo lifecycle events for audit and replay

#### UserPreferences Entity
- **Fields**:
  - user_id: UUID (primary key)
  - notification_channels: JSON (preferred channels)
  - advance_notification_minutes: Integer (default 15)
  - do_not_disturb_start: Time (nullable)
  - do_not_disturb_end: Time (nullable)
  - timezone: String (default UTC)
  - created_at: DateTime
  - updated_at: DateTime
- **Relationships**: Links to User entity

### API Contracts

#### Todo Service API (REST)
```
POST /api/v1/todos
{
  "title": "string",
  "description": "string",
  "deadline": "ISO8601 datetime",
  "priority": "high|normal|low",
  "user_id": "string"
}

PUT /api/v1/todos/{todo_id}
{
  "title": "string",
  "description": "string",
  "deadline": "ISO8601 datetime",
  "priority": "high|normal|low"
}

DELETE /api/v1/todos/{todo_id}

GET /api/v1/todos/{todo_id}
```

#### User Preferences API (REST)
```
GET /api/v1/users/{user_id}/preferences
GET /api/v1/users/{user_id}/notifications

PUT /api/v1/users/{user_id}/preferences
{
  "notification_channels": ["email", "sms", "push"],
  "advance_notification_minutes": 15,
  "do_not_disturb_start": "HH:MM",
  "do_not_disturb_end": "HH:MM",
  "timezone": "UTC"
}
```

### Kafka Event Contracts

#### Todo Created Event
```
Topic: todo.created
Key: user_id
Value: {
  "todo_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "description": "string",
  "deadline": "ISO8601 datetime",
  "priority": "string",
  "created_at": "ISO8601 datetime"
}
```

#### Deadline Scheduled Event
```
Topic: deadline.scheduled
Key: user_id
Value: {
  "schedule_id": "uuid",
  "todo_id": "uuid",
  "user_id": "uuid",
  "deadline": "ISO8601 datetime",
  "scheduled_time": "ISO8601 datetime",
  "notification_type": "reminder|deadline|overdue"
}
```

#### Notification Request Event
```
Topic: notification.request
Key: user_id
Value: {
  "notification_id": "uuid",
  "todo_id": "uuid",
  "user_id": "uuid",
  "title": "string",
  "message": "string",
  "deadline": "ISO8601 datetime",
  "channels": ["email", "sms", "push"],
  "priority": "high|normal|low"
}
```

## Phase 2: Implementation Strategy

### Service Development Order

1. **Shared Libraries** (Week 1)
   - Create shared schemas and Kafka configuration
   - Set up common utilities and error handling

2. **Todo Service** (Week 2)
   - Implement basic todo CRUD operations
   - Integrate Kafka producer for events
   - Connect to database

3. **Scheduler Service** (Week 3)
   - Implement event consumer for todo events
   - Build scheduling logic with APScheduler
   - Create job persistence layer
   - Handle todo updates/deletions

4. **Notification Service** (Week 4)
   - Implement event consumer for notification requests
   - Build notification delivery mechanisms
   - Add retry logic and error handling

5. **User Service** (Week 5)
   - Implement user preferences management
   - Integrate with notification service

6. **Integration & Testing** (Week 6)
   - End-to-end testing
   - Performance testing
   - Failure scenario testing

### Development Approach

- Each service developed as independent modules
- Container-first development with Docker
- Environment-specific configurations
- Comprehensive logging and monitoring
- Automated testing at unit and integration levels

### Deployment Strategy

- Docker Compose for local development
- Kubernetes-ready manifests for production
- Environment-specific configurations
- Health checks and liveness probes
- Resource limits and scaling configurations

## Risk Assessment

### High-Risk Areas
1. **Clock synchronization** across distributed services
2. **Kafka availability** affecting notification delivery
3. **Notification delivery reliability** across different channels
4. **Database performance** under high load

### Mitigation Strategies
1. Use UTC for all timestamps and implement proper timezone conversion
2. Configure Kafka with appropriate replication and acknowledgment settings
3. Implement robust retry mechanisms with exponential backoff
4. Design efficient database indexes and query patterns

## Success Criteria Verification

Each success criterion from the spec will be verified through:
- **SC-001**: Timing measurements in integration tests
- **SC-002**: Load testing with simulated concurrent notifications
- **SC-003**: User feedback collection mechanisms
- **SC-004**: Uptime monitoring and reporting
- **SC-005**: Delivery success rate tracking
- **SC-006**: Throughput benchmarking
- **SC-007**: Failure recovery testing

This implementation plan provides a structured approach to building the Kafka-based event-driven deadline notification system while adhering to the architectural requirements and success criteria defined in the specification.