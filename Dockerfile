FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src
RUN mkdir -p /app/data
ENV DATA_PATH=/app/data
ENV PORT=5000
EXPOSE 5000
CMD ["gunicorn", "app:app", "--chdir", "src", "--bind", "0.0.0.0:5000", "--workers", "1"]
