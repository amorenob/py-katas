FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install basic packages for code execution
RUN pip install --no-cache-dir --upgrade pip

# Create a non-root user for security
RUN adduser --disabled-password --gecos "" coderunner

# Switch to non-root user
USER coderunner

# Set environment variables for security
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python"]