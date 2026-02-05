# TodoList Pro - Full Stack Application with AI Features

TodoList Pro is a comprehensive task management application featuring modern web technologies and AI integration.

## 🚀 Features

### Core Features
- **Task Management**: Create, update, complete, and delete tasks
- **Deadline Tracking**: Set deadlines with calendar integration and time picker
- **Visual Indicators**: Color-coded deadline badges showing overdue, today's, and future deadlines
- **Responsive UI**: Works on desktop and mobile devices

### AI-Powered Features
- **AI Chatbot**: Natural language interaction for task management
- **Voice Assistant**: Voice-controlled task creation and management
- **Intelligent Prioritization**: AI-powered task suggestions

### Notification System
- **Kafka-Based**: Event-driven architecture for scalable notifications
- **Deadline Reminders**: Automatic notifications before deadlines
- **Multi-Channel Delivery**: Email, SMS, and push notifications
- **Smart Scheduling**: Configurable reminder timing
- **Reliability Features**: Retry mechanisms and dead letter queue

## 🛠 Tech Stack

### Frontend
- **Next.js 16**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Reusable UI components
- **TanStack Query**: Server state management
- **Lucide React**: Beautiful SVG icons

### Backend
- **FastAPI**: Modern Python web framework
- **SQLModel**: SQL database modeling
- **PostgreSQL**: Production-grade database
- **AsyncPG**: Async PostgreSQL driver
- **Pydantic**: Data validation and settings management
- **Kafka**: Event streaming platform

### Authentication
- **Better Auth**: Modern authentication solution
- **JWT Tokens**: Secure session management

### AI Integration
- **Google Generative AI**: Large language model integration
- **MCP SDK**: Claude integration for AI chatbot

## 📋 Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **PostgreSQL** 12+
- **Kafka** 2.x+
- **Docker** (optional, for easier setup)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd todolist-pro
```

### 2. Backend Setup
```bash
cd backend/hf-deploy
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Create .env file with your configuration
cat > .env << EOF
DATABASE_URL=postgresql://username:password@localhost/todolist_pro
BETTER_AUTH_SECRET=your-super-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_ENABLED=true
EOF

# Run database migrations
uv run alembic upgrade head

# Start the backend
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install

# Create .env.local file
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
EOF

# Start the frontend
npm run dev
```

### 4. Kafka Setup
```bash
# Start ZooKeeper (if not already running)
zookeeper-server-start $KAFKA_HOME/config/zookeeper.properties

# Start Kafka (if not already running)
kafka-server-start $KAFKA_HOME/config/server.properties

# Create required topics
kafka-topics --create --topic todo.created --bootstrap-server localhost:9092
kafka-topics --create --topic todo.updated --bootstrap-server localhost:9092
kafka-topics --create --topic todo.deleted --bootstrap-server localhost:9092
kafka-topics --create --topic notification.request --bootstrap-server localhost:9092
kafka-topics --create --topic notification.sent --bootstrap-server localhost:9092
kafka-topics --create --topic notification.failed --bootstrap-server localhost:9092
```

### 5. Notification Services Setup
```bash
cd kafka-todo-notification-system

# Run the scheduler service (in a new terminal)
cd scheduler-service
python -m app.main

# Run the notification service (in a new terminal)
cd notification-service
python -m app.main
```

### 6. Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs

## 🔐 Authentication

The application uses Better Auth for secure authentication:
- Registration with email verification
- JWT-based session management
- Protected API routes
- User isolation for data privacy

## 🤖 AI Features

### Chatbot
- Natural language task management
- Context-aware responses
- Task creation and modification via chat
- Integration with MCP SDK

### Voice Assistant
- Speech-to-text for hands-free task creation
- Text-to-speech for notifications
- Voice command recognition
- Integration with backend services

## 📅 Deadline Notifications

The Kafka-based notification system provides:
- **Automatic Reminders**: Configurable timing before deadlines
- **Multi-Channel Delivery**: Email, SMS, and push notifications
- **Smart Scheduling**: Handles task updates and cancellations
- **Reliability**: Retry mechanisms and dead letter queue
- **Scalability**: Event-driven architecture handles high loads

## 🏗 Architecture

### Event-Driven Design
- Kafka topics for decoupled service communication
- Real-time task lifecycle notifications
- Independent service scaling
- Resilient system design

### Microservices Pattern
- Frontend: Next.js application
- Backend: FastAPI service
- Notification Scheduler: Task deadline management
- Notification Service: Multi-channel delivery
- Database: PostgreSQL for persistence

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
```

### Backend Tests
```bash
cd backend/hf-deploy
uv run pytest
```

## 🚢 Deployment

### Local Kubernetes Setup (Minikube + Helm)
Deploy TodoList Pro to a local Kubernetes cluster using Minikube and Helm:

```bash
# Start Minikube with sufficient resources
minikube start --cpus=2 --memory=4096 --driver=docker

# Enable ingress addon (optional)
minikube addons enable ingress

# Build container images in Minikube's Docker environment
eval $(minikube docker-env)
docker build -t todolist-frontend:local ./frontend
docker build -t todolist-backend:local ./backend

# Create local values file with secrets
cp helm/todolist/values-local.yaml.example values-local.yaml
# Edit values-local.yaml to add your database URL and auth secret

# Deploy using Helm
helm upgrade --install todolist ./helm/todolist -f values-local.yaml

# Access the application
minikube service todolist-frontend --url
```

For detailed Kubernetes deployment instructions, see [README-K8S.md](README-K8S.md).

### Docker Setup
```bash
# Build and start all services
docker-compose up --build

# Or deploy individual services to cloud platforms
```

### Environment Variables
Both frontend and backend require environment variables for:
- Database connection
- Authentication secrets
- AI API keys
- Kafka configuration
- Third-party service credentials

## 🔧 Configuration

### Frontend Configuration
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_BETTER_AUTH_URL`: Auth service URL
- `NEXT_PUBLIC_GEMINI_API_KEY`: (if using direct API calls)

### Backend Configuration
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Authentication secret
- `GEMINI_API_KEY`: Google Generative AI API key
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `KAFKA_ENABLED`: Enable/disable Kafka integration

## 📊 API Documentation

The backend provides comprehensive API documentation at `/docs` endpoint:
- Interactive API explorer
- Request/response examples
- Authentication requirements
- Error handling details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository.

---

Built with ❤️ using modern web technologies.