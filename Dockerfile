# Use official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies including PostgreSQL development libraries
RUN apt-get update && \
    apt-get install -y gcc python3-dev musl-dev postgresql-client libpq-dev

# Set the working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy Django project files into the working directory
COPY . .

# Expose the port on which the app runs
EXPOSE 8000

# Run gunicorn server
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]

