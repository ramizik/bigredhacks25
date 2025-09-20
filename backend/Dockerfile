# WonderKid Reading Game Backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Accept build arguments for environment variables
ARG GOOGLE_API_KEY
ARG MONGODB_URI
ARG JWT_SECRET_KEY

# Set environment variables from build args (for build-time tests)
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV MONGODB_URI=${MONGODB_URI}
ENV JWT_SECRET_KEY=${JWT_SECRET_KEY}

# Set environment variables to force PEP 517 mode and avoid gRPC build issues
ENV PIP_USE_PEP517=true
ENV GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
ENV GRPC_PYTHON_BUILD_WITH_CYTHON=1

# Install system dependencies for AI processing and image generation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    pkg-config \
    libssl-dev \
    build-essential \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for generated files
RUN mkdir -p /app/media/illustrations /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port (Google Cloud Run uses 8080)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
