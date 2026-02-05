# Testing Plan for Kafka-based Deadline Notification System

## 1. Unit Tests

### Todo Service Unit Tests

#### Test Todo Creation
```python
def test_create_todo_success():
    """Test successful todo creation"""
    # Mock input data
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description",
        "deadline": "2024-12-31T23:59:59Z",
        "priority": "normal",
        "user_id": "test-user-id"
    }

    # Call create_todo endpoint
    response = client.post("/api/v1/todos", json=todo_data)

    # Assertions
    assert response.status_code == 200
    assert response.json()["title"] == "Test Todo"
    assert response.json()["user_id"] == "test-user-id"

    # Verify Kafka event was published
    # (using mocking to verify publish call)
```

#### Test Todo Update
```python
def test_update_todo_success():
    """Test successful todo update"""
    # Create initial todo
    initial_todo = {
        "title": "Initial Title",
        "description": "Initial Description",
        "deadline": "2024-12-31T23:59:59Z",
        "priority": "normal",
        "user_id": "test-user-id"
    }

    # Update todo
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description"
    }

    response = client.put("/api/v1/todos/test-todo-id", json=update_data)

    # Assertions
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
```

### Scheduler Service Unit Tests

#### Test Notification Scheduling
```python
def test_schedule_notification():
    """Test scheduling a notification"""
    scheduler = SchedulerService()

    # Mock event data
    event_data = {
        "todo_id": "test-todo-id",
        "user_id": "test-user-id",
        "title": "Test Todo",
        "deadline": "2024-12-31T23:59:59Z"
    }

    # Call scheduling function
    await scheduler.handle_todo_created(event_data)

    # Assertions
    # Verify notification was scheduled
    assert len(scheduler.scheduled_notifications) > 0

    # Verify Kafka event was published
    # (using mocking to verify publish call)
```

### Notification Service Unit Tests

#### Test Email Sending
```python
def test_send_email_notification():
    """Test sending email notification"""
    notification_service = NotificationService()

    # Mock event data
    event = NotificationRequestEvent(
        notification_id="test-notification-id",
        todo_id="test-todo-id",
        user_id="test-user-id",
        title="Test Todo",
        message="Test message",
        deadline=datetime.now(),
        channels=["email"]
    )

    # Call send function
    await notification_service.send_email_notification(event)

    # Assertions
    # Verify email was sent (using mocking)
```

## 2. Integration Tests

### End-to-End Workflow Test
```python
def test_full_notification_workflow():
    """Test the full workflow from todo creation to notification"""
    # 1. Create a todo with a deadline
    todo_data = {
        "title": "Test Todo",
        "deadline": (datetime.now() + timedelta(seconds=2)).isoformat(),  # 2 seconds in future
        "priority": "normal",
        "user_id": "test-user-id"
    }

    response = client.post("/api/v1/todos", json=todo_data)
    assert response.status_code == 200
    todo_id = response.json()["id"]

    # 2. Wait for scheduler to process the event
    time.sleep(3)  # Allow time for processing

    # 3. Verify notification was scheduled
    # This would involve checking the scheduler's internal state or DB

    # 4. Wait for deadline to pass and notification to be sent
    time.sleep(3)  # Allow time for deadline to pass

    # 5. Verify notification was sent
    # This would involve checking mocks or logs
```

### Kafka Integration Test
```python
def test_kafka_message_flow():
    """Test message flow through Kafka topics"""
    # Create test consumer for each topic
    consumer = KafkaConsumer(
        KafkaConfig.TOPIC_TODO_CREATED,
        KafkaConfig.TOPIC_DEADLINE_SCHEDULED,
        KafkaConfig.TOPIC_NOTIFICATION_REQUEST,
        bootstrap_servers=KafkaConfig.BOOTSTRAP_SERVERS,
        group_id="test-consumer-group",
        auto_offset_reset='earliest'
    )

    # Create a todo
    todo_data = {
        "title": "Integration Test Todo",
        "deadline": (datetime.now() + timedelta(minutes=1)).isoformat(),
        "priority": "normal",
        "user_id": "test-user-id"
    }

    response = client.post("/api/v1/todos", json=todo_data)
    assert response.status_code == 200

    # Consume messages and verify the flow
    messages_received = []
    for message in consumer:
        messages_received.append(json.loads(message.value.decode('utf-8')))
        if len(messages_received) >= 3:  # Expect at least 3 messages
            break

    # Verify expected message types were received
    event_types = [msg.get('todo_id') for msg in messages_received]
    assert len(event_types) >= 2  # At least todo created and deadline scheduled
```

## 3. Failure Scenarios Tests

### Service Restart Test
```python
def test_scheduler_service_restart():
    """Test scheduler service handles restart gracefully"""
    # Start scheduler service
    scheduler_process = subprocess.Popen(["python", "scheduler-service/app/main.py"])

    # Create a todo with a deadline in 1 minute
    todo_data = {
        "title": "Restart Test Todo",
        "deadline": (datetime.now() + timedelta(minutes=1)).isoformat(),
        "priority": "normal",
        "user_id": "test-user-id"
    }

    response = client.post("/api/v1/todos", json=todo_data)
    assert response.status_code == 200

    # Wait for scheduler to process
    time.sleep(2)

    # Restart scheduler service
    scheduler_process.terminate()
    scheduler_process.wait()

    # Restart scheduler
    scheduler_process = subprocess.Popen(["python", "scheduler-service/app/main.py"])

    # Wait for deadline to pass
    time.sleep(70)  # Wait 1 minute and 10 seconds

    # Verify notification was still sent despite restart
    # (would need to check notification logs or state)
```

### Kafka Broker Failure Test
```python
def test_kafka_broker_failure():
    """Test system behavior when Kafka broker fails"""
    # Start with healthy Kafka
    # Create a few todos

    # Simulate Kafka failure
    # (would require container orchestration or specific setup)

    # Create more todos during failure

    # Restore Kafka
    # Verify all events are processed eventually
```

## 4. Load Testing

### Concurrent Todo Creation Test
```python
def test_concurrent_todo_creation():
    """Test system under concurrent load"""
    import asyncio
    import aiohttp

    async def create_todo(session, todo_data):
        async with session.post("http://localhost:8000/api/v1/todos", json=todo_data) as response:
            return await response.json()

    async def run_load_test():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(100):  # Create 100 todos concurrently
                todo_data = {
                    "title": f"Load Test Todo {i}",
                    "deadline": (datetime.now() + timedelta(hours=1)).isoformat(),
                    "priority": "normal",
                    "user_id": f"test-user-{i}"
                }
                task = create_todo(session, todo_data)
                tasks.append(task)

            results = await asyncio.gather(*tasks)
            assert len(results) == 100

    asyncio.run(run_load_test())
```

## 5. Notification Delivery Tests

### Retry Logic Test
```python
def test_notification_retry_logic():
    """Test notification retry mechanism"""
    # Mock notification service to fail initially
    # Verify retries occur with proper backoff
    # Verify eventual success or failure marking
```

### Multiple Channel Test
```python
def test_multiple_notification_channels():
    """Test notifications sent through multiple channels"""
    # Create todo with notification preferences for email, sms, and push
    # Verify all channels are attempted
    # Verify appropriate fallbacks
```

## 6. Data Consistency Tests

### Event Ordering Test
```python
def test_event_ordering():
    """Test that events are processed in correct order"""
    # Create todo, update it, then delete it rapidly
    # Verify the final state is consistent
```

### Duplicate Prevention Test
```python
def test_duplicate_prevention():
    """Test that duplicate events don't cause issues"""
    # Send the same event twice
    # Verify system handles it gracefully without duplicates
```

## 7. Monitoring and Alerting Tests

### Health Check Test
```python
def test_health_checks():
    """Test health check endpoints"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

These tests cover the essential functionality, failure scenarios, and edge cases for the Kafka-based deadline notification system. They ensure reliability, scalability, and correctness of the implemented solution.