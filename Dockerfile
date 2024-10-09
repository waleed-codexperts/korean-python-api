# Use an official Ubuntu base image
FROM ubuntu:20.04

# Set environment variables to prevent interaction during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    cmake \
    build-essential \
    g++ \
    libssl-dev \
    libffi-dev \
    python3-dev \
    curl

# Install FastAPI-related Python dependencies
# Copy the requirements.txt file into the container
COPY requirements.txt /app/requirements.txt

# Set working directory
WORKDIR /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt



# Copy the FastAPI app into the container
COPY . /app

# Run the FastAPI app
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["fastapi","run", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# Expose the port FastAPI will run on
EXPOSE 8000