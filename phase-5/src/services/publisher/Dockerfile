FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY services/publisher/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY shared/ /app/shared/

# Copy application
COPY services/publisher/app.py .

EXPOSE 5000

ENV APP_PORT=5000
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:app"]
