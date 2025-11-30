FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src
COPY data/ ./data
COPY uploads/ ./uploads

# Environment variables
ENV DATA_PATH=/app/data
ENV UPLOAD_FOLDER=/app/uploads
ENV PORT=5000

EXPOSE 5000

# Start Flask app with Gunicorn inside src/
CMD ["gunicorn", "app:app", "--chdir", "src", "--bind", "0.0.0.0:5000", "--workers", "1"]
