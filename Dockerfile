FROM python:3.13 AS python-base

WORKDIR /alphasignal

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock (if available)
COPY pyproject.toml poetry.lock* /app/

# Configure Poetry to install dependencies into the global environment
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Copy the full project
COPY . .

# Expose port 8000 (used by your FastAPI app)
EXPOSE 8000

# Default command (will be overridden by docker-compose services)
CMD ["python", "alphasignal/app.py"]