FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/
COPY alembic.ini .
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

# Expose port
EXPOSE 8001

ENTRYPOINT ["./entrypoint.sh"]

