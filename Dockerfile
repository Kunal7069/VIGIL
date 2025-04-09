# Use official Python base image
FROM python:3.12-slim

# Set env vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=1.8.2

# Install Poetry and system tools
RUN apt-get update && apt-get install -y curl \
 && curl -sSL https://install.python-poetry.org | python3 - \
 && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy pyproject and lock file
COPY pyproject.toml poetry.lock* ./

# Install dependencies without virtualenv
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi

# Copy app source
COPY . .

# Set working directory to src to run main.py directly
WORKDIR /app/src

# Expose the port (default)
EXPOSE 8000

# Command to run FastAPI app with Uvicorn, using env PORT
CMD ["python", "main.py"]
