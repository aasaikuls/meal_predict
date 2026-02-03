FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY ai_summary.py .
COPY meal_planning.py .

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "main.py"]
