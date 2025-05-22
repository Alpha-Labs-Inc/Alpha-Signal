FROM python:3.13.1-slim AS python-base

WORKDIR /alphasignal
ENV PYTHONPATH=/alphasignal

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock (if available)
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root

# Copy the full project
COPY . .
RUN chmod +x start_backend.sh   # Ensure startup script is executable

# Expose port 8000 (used by your FastAPI app)
EXPOSE 8000

# Default command (will be overridden by docker-compose services)
CMD ["python", "alphasignal/app.py"]