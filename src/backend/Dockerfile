# ---- Builder Stage ----
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies needed for building wheels
RUN apt-get update && apt-get install -y build-essential curl

# Install uv
RUN pip install uv

# Copy requirements and install dependencies into a virtual environment
COPY pyproject.toml ./
COPY requirements.txt ./
RUN uv venv .venv && . .venv/bin/activate && uv pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/backend/ ./

# ---- Runner Stage ----
FROM python:3.11-slim as runner

WORKDIR /app

# Create a non-root user
RUN useradd --create-home appuser
USER appuser

# Copy virtual environment and application code from builder stage
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /app ./

# Activate virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]