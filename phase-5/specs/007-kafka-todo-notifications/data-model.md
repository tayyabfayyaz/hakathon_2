# Data Model: Kafka-based Event-Driven Deadline Notification System

## Entity Relationships

```
Todo ───(1 to many)─── ScheduledNotification
 ↑                           │
 │(many to 1)                │(many to 1)
 │                           ↓
User ───(1 to 1)─── UserPreferences
     │
     │(1 to many)
     ↓
NotificationRequest ───(1 to 1)─── TodoEvent
```

## Entity Definitions

### Todo Entity
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Not Null | Unique identifier for the todo |
| user_id | UUID | Foreign Key, Not Null | Reference to the user who owns this todo |
| title | String(255) | Not Null | Title of the todo |
| description | Text | Nullable | Detailed description of the todo |
| deadline | DateTime | Nullable | Deadline for the todo |
| priority | String | Default: "normal", Enum: low/normal/high | Priority level of the todo |
| status | String | Default: "pending", Enum: pending/completed/deleted | Current status of the todo |
| created_at | DateTime | Not Null, Auto-generated | Timestamp when the todo was created |
| updated_at | DateTime | Not Null, Auto-generated, Updates on change | Timestamp when the todo was last updated |

**Indexes:**
- idx_todos_user_id (user_id)
- idx_todos_deadline (deadline)
- idx_todos_status (status)

### ScheduledNotification Entity
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Not Null | Unique identifier for the scheduled notification |
| todo_id | UUID | Foreign Key, Not Null | Reference to the associated todo |
| user_id | UUID | Foreign Key, Not Null | Reference to the user receiving the notification |
| scheduled_time | DateTime | Not Null | Time when the notification should be sent |
| notification_type | String | Not Null, Enum: reminder/deadline/overdue | Type of notification |
| status | String | Default: "pending", Enum: pending/triggered/sent/failed | Current status of the scheduled notification |
| created_at | DateTime | Not Null, Auto-generated | Timestamp when the schedule was created |
| processed_at | DateTime | Nullable | Timestamp when the notification was processed |

**Indexes:**
- idx_scheduled_notifications_time (scheduled_time)
- idx_scheduled_notifications_todo (todo_id)
- idx_scheduled_notifications_user (user_id)
- idx_scheduled_notifications_status (status)

### NotificationRequest Entity
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Not Null | Unique identifier for the notification request |
| todo_id | UUID | Foreign Key, Not Null | Reference to the associated todo |
| user_id | UUID | Foreign Key, Not Null | Reference to the user receiving the notification |
| title | String(255) | Not Null | Title of the associated todo |
| message | Text | Not Null | Content of the notification message |
| deadline | DateTime | Not Null | Original deadline of the todo |
| channels | JSON | Not Null | List of notification channels to use |
| priority | String | Default: "normal", Enum: low/normal/high | Priority level of the notification |
| status | String | Default: "pending", Enum: pending/processing/sent/failed | Current status of the notification request |
| created_at | DateTime | Not Null, Auto-generated | Timestamp when the request was created |
| sent_at | DateTime | Nullable | Timestamp when the notification was sent |

**Indexes:**
- idx_notification_requests_todo (todo_id)
- idx_notification_requests_user (user_id)
- idx_notification_requests_status (status)

### TodoEvent Entity
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key, Not Null | Unique identifier for the event |
| todo_id | UUID | Foreign Key, Not Null | Reference to the associated todo |
| user_id | UUID | Foreign Key, Not Null | Reference to the user associated with the todo |
| event_type | String | Not Null, Enum: created/updated/deleted | Type of the event |
| payload | JSON | Not Null | Event data containing the todo information |
| created_at | DateTime | Not Null, Auto-generated | Timestamp when the event was created |

**Indexes:**
- idx_todo_events_todo (todo_id)
- idx_todo_events_user (user_id)
- idx_todo_events_type (event_type)
- idx_todo_events_time (created_at)

### UserPreferences Entity
| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| user_id | UUID | Primary Key, Not Null, Foreign Key | Reference to the user |
| notification_channels | JSON | Not Null | List of preferred notification channels |
| advance_notification_minutes | Integer | Default: 15, Range: 1-10080 (7 days) | Minutes before deadline to send reminder |
| do_not_disturb_start | Time | Nullable | Start time for do-not-disturb period |
| do_not_disturb_end | Time | Nullable | End time for do-not-disturb period |
| timezone | String | Default: "UTC" | User's preferred timezone |
| created_at | DateTime | Not Null, Auto-generated | Timestamp when preferences were created |
| updated_at | DateTime | Not Null, Auto-generated, Updates on change | Timestamp when preferences were last updated |

## State Transition Diagrams

### ScheduledNotification States
```
PENDING → TRIGGERED → SENT
     ↓         ↓        ↓
   FAILED ←─────────────┘
```

### NotificationRequest States
```
PENDING → PROCESSING → SENT
     ↓         ↓         ↓
   FAILED ←──────────────┘
```

### Todo States
```
PENDING → COMPLETED
    ↓         ↓
  DELETED ←───┘
```

## Validation Rules

### Todo Entity
- Title must not be empty
- Deadline must be in the future if provided
- Priority must be one of the allowed values
- Status must be one of the allowed values

### ScheduledNotification Entity
- scheduled_time must be in the future
- notification_type must be one of the allowed values
- status must be one of the allowed values

### NotificationRequest Entity
- channels must contain at least one valid channel
- priority must be one of the allowed values
- status must be one of the allowed values

### UserPreferences Entity
- notification_channels must contain at least one valid channel
- advance_notification_minutes must be between 1 and 10080 (7 days)
- timezone must be a valid IANA timezone identifier
- do_not_disturb_end must be after do_not_disturb_start if both are set