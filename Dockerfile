
# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install uv
RUN pip install uv

# Copy the entire project
COPY . .

# Sync dependencies for all components during build
# This ensures dependencies are cached in the image
RUN uv sync
RUN cd backend && uv sync
RUN cd frontend && uv sync

# Expose ports
# 5000: Frontend
# 5001: Backend
EXPOSE 5000
EXPOSE 5001

# Run the integrated startup script
CMD ["uv", "run", "python", "main.py"]
