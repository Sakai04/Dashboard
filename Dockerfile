# Base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Install curl
RUN apt-get update && apt-get install -y curl


# Copy requirements.txt into the container
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir docker

# Copy the rest of the application code into the container
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the FastAPI server
