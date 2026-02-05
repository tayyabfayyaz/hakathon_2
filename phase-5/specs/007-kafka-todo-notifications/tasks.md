# Implementation Tasks: Kafka-based Event-Driven Deadline Notification System

## Feature Overview
This document outlines the implementation tasks for a Kafka-based event-driven deadline notification system for the AI-powered Todo application. The system will consist of multiple microservices communicating through Apache Kafka to provide scalable, reliable notifications for todo deadlines.

## Phase 1: Setup Tasks
**Goal**: Establish project structure and foundational infrastructure

- [x] T001 Create project directory structure with shared, todo-service, scheduler-service, notification-service, and user-service modules
- [x] T002 Set up shared schemas module with event definitions and models in shared/schemas/
- [x] T003 Configure Kafka connection settings in shared/kafka_config/
- [x] T004 Initialize database connection utilities in shared/database/
- [x] T005 Set up Docker configuration files for all services
- [x] T006 Create docker-compose.yml with Kafka, Zookeeper, and PostgreSQL services
- [x] T007 Install required dependencies for each service in requirements.txt files

## Phase 2: Foundational Tasks
**Goal**: Implement shared components and foundational services that block all user stories

- [x] T008 [P] Create common utility functions in shared/utils/
- [x] T009 [P] Implement error handling and logging utilities in shared/errors.py and shared/logging.py
- [x] T010 [P] Create database models for all entities in shared/database/models.py
- [x] T011 [P] Set up database migration scripts in shared/database/migrations/
- [x] T012 [P] Implement database connection pool in shared/database/connection.py
- [x] T013 [P] Create Kafka producer wrapper in shared/kafka/producer.py
- [x] T014 [P] Create Kafka consumer wrapper in shared/kafka/consumer.py
- [x] T015 [P] Define all Kafka topic constants in shared/kafka/topics.py
- [x] T016 [P] Create event serializer/deserializer in shared/kafka/serializer.py
- [x] T017 Set up API response models in shared/api/responses.py

## Phase 3: User Story 1 - Receive Deadline Reminders (Priority: P1)
**Goal**: Implement the core functionality for users to receive timely reminders about upcoming todo deadlines

**Independent Test Criteria**: Can be fully tested by creating a todo with a deadline and verifying that a notification is sent before the deadline. Delivers immediate value of timely task completion.

**Tasks**:

- [x] T018 [US1] Create Todo model in todo-service/app/models/todo.py
- [x] T019 [US1] Create ScheduledNotification model in todo-service/app/models/scheduled_notification.py
- [x] T020 [US1] Create UserPreferences model in todo-service/app/models/user_preferences.py
- [x] T021 [US1] Implement Todo CRUD operations in todo-service/app/api/todos.py
- [x] T022 [US1] Implement User Preferences API in todo-service/app/api/preferences.py
- [x] T023 [US1] Add Kafka producer to Todo creation endpoint to publish todo.created events
- [x] T024 [US1] Create Scheduler service main application in scheduler-service/app/main.py
- [x] T025 [US1] Implement Kafka consumer for todo.created events in scheduler-service/app/consumers/todo_consumer.py
- [x] T026 [US1] Create notification scheduling logic in scheduler-service/app/scheduler/notifications.py
- [x] T027 [US1] Implement APScheduler job creation for reminder notifications
- [x] T028 [US1] Create job persistence layer to survive service restarts
- [x] T029 [US1] Implement notification request publisher to send to notification.request topic
- [x] T030 [US1] Create Notification service main application in notification-service/app/main.py
- [x] T031 [US1] Implement Kafka consumer for notification.request events in notification-service/app/consumers/notification_consumer.py
- [x] T032 [US1] Create email notification provider in notification-service/app/providers/email.py
- [x] T033 [US1] Create basic notification delivery logic in notification-service/app/services/notification_service.py
- [x] T034 [US1] Add notification status tracking in notification-service
- [x] T035 [US1] Implement timezone handling for global users
- [x] T036 [US1] Test User Story 1 acceptance scenario: Given user creates a todo with a deadline, When deadline approaches, Then user receives a reminder notification

## Phase 4: User Story 2 - Receive Deadline Reached Notifications (Priority: P1)
**Goal**: Implement functionality for users to receive notifications when a deadline is reached

**Independent Test Criteria**: Can be tested by creating a todo with a past deadline and verifying that a "deadline reached" notification is sent. Provides immediate value of deadline awareness.

**Tasks**:

- [x] T037 [US2] Enhance scheduler service to create deadline notification jobs (at exact deadline time)
- [x] T038 [US2] Update notification scheduling logic to handle both reminder and deadline notifications
- [x] T039 [US2] Modify Kafka event publishing to include both reminder and deadline scheduled events
- [x] T040 [US2] Create SMS notification provider in notification-service/app/providers/sms.py
- [x] T041 [US2] Add SMS delivery capability to notification service
- [x] T042 [US2] Create push notification provider in notification-service/app/providers/push.py
- [x] T043 [US2] Add push notification delivery capability
- [x] T044 [US2] Implement configurable notification channels based on user preferences
- [x] T045 [US2] Update UserPreferences model to support multiple channels
- [x] T046 [US2] Test User Story 2 acceptance scenario: Given user has a todo with a deadline, When deadline time is reached, Then user receives a deadline reached notification

## Phase 5: User Story 3 - Handle Missed Deadlines (Priority: P2)
**Goal**: Implement functionality to handle missed deadlines appropriately with follow-up notifications

**Independent Test Criteria**: Can be tested by allowing a deadline to pass and verifying that overdue notifications are sent according to user preferences.

**Tasks**:

- [x] T047 [US3] Enhance scheduler service to detect and handle missed deadlines
- [x] T048 [US3] Create overdue notification scheduling logic
- [x] T049 [US3] Implement logic to send overdue notifications based on user preferences
- [x] T050 [US3] Add configurable follow-up timing for overdue notifications
- [x] T051 [US3] Create job cancellation logic when todos are updated or deleted
- [x] T052 [US3] Implement todo.updated event consumer in scheduler service
- [x] T053 [US3] Implement todo.deleted event consumer in scheduler service
- [x] T054 [US3] Add logic to cancel scheduled notifications when todos are deleted
- [x] T055 [US3] Test User Story 3 acceptance scenario: Given user has missed a deadline, When configured follow-up time elapses, Then user receives overdue reminder notification

## Phase 6: Enhanced Features & Reliability
**Goal**: Implement advanced features and reliability mechanisms

- [x] T056 Implement retry mechanism for failed notifications with exponential backoff
- [x] T057 Create dead letter queue for permanently failed notifications
- [x] T058 Add do-not-disturb hour handling based on user preferences
- [x] T059 Implement configurable advance notification timing (1 minute to 7 days)
- [ ] T060 Add comprehensive logging and monitoring for all services
- [ ] T061 Implement health check endpoints for all services
- [ ] T062 Create metrics collection for notification delivery success rates
- [ ] T063 Add circuit breaker pattern for external service calls

## Phase 7: Polish & Cross-Cutting Concerns
**Goal**: Complete the system with testing, documentation, and deployment configurations

- [x] T064 Write unit tests for all core functionality
- [x] T065 Write integration tests for the complete event flow
- [x] T066 Create end-to-end test suite for all user stories
- [ ] T067 Document API endpoints with examples
- [ ] T068 Create deployment guides for different environments
- [ ] T069 Set up proper error handling and graceful degradation
- [ ] T070 Optimize database queries and add proper indexing
- [ ] T071 Configure proper resource limits and scaling settings
- [ ] T072 Perform load testing to verify system can handle 10,000 concurrent scheduled notifications
- [ ] T073 Create monitoring dashboards for notification delivery metrics
- [x] T074 Final integration testing and validation against success criteria

## Dependencies

### User Story Dependencies
- User Story 2 depends on User Story 1 (requires basic notification infrastructure)
- User Story 3 depends on User Story 1 and 2 (requires complete notification infrastructure)

### Service Dependencies
- Todo Service depends on Kafka and PostgreSQL
- Scheduler Service depends on Kafka, PostgreSQL, and Todo Service events
- Notification Service depends on Kafka and user preferences from Todo Service

## Parallel Execution Opportunities

### Within User Story 1:
- [P] Tasks T018-T020 (model creation) can be done in parallel
- [P] Tasks T032, T033 (notification providers) can be developed in parallel
- [P] Services (Todo, Scheduler, Notification) can be developed in parallel

### Within User Story 2:
- [P] Tasks T040, T041, T042, T043 (notification channel providers) can be developed in parallel

## Implementation Strategy

### MVP Scope (User Story 1 Only):
- Basic todo creation with deadlines
- Simple reminder notifications 15 minutes before deadline
- Email delivery only
- Basic Kafka integration
- Minimal UI for testing

### Incremental Delivery:
1. Complete User Story 1 as MVP
2. Add User Story 2 functionality (deadline notifications)
3. Add User Story 3 functionality (missed deadlines)
4. Enhance with additional features and reliability mechanisms

This task breakdown ensures that each user story can be developed and tested independently while maintaining the necessary dependencies between them.