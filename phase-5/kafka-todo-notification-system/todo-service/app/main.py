from fastapi import FastAPI
from .api.todos import router as todos_router
from .api.preferences import router as preferences_router
from shared.api.responses import HealthCheckResponse
from datetime import datetime
import time

app = FastAPI(title="Todo Service", version="1.0.0")

# Register API routes
app.include_router(todos_router)
app.include_router(preferences_router)

# Start time for uptime calculation
start_time = time.time()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    uptime_seconds = time.time() - start_time
    uptime_str = f"{uptime_seconds:.2f} seconds"

    return HealthCheckResponse(
        success=True,
        message="Todo Service is healthy",
        service="todo-service",
        version="1.0.0",
        uptime=uptime_str
    )


@app.on_event("startup")
def startup_event():
    """Startup event handler."""
    print("Todo Service starting up...")
    # Initialize Kafka producer
    from shared.kafka.producer import get_kafka_producer
    get_kafka_producer()

    # Initialize database
    from shared.database.migrations import migrate_database
    migrate_database()


@app.on_event("shutdown")
def shutdown_event():
    """Shutdown event handler."""
    print("Todo Service shutting down...")
    # Close Kafka producer if exists
    from shared.kafka.producer import producer_instance
    if producer_instance:
        producer_instance.close()