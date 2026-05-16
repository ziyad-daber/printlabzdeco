# Use official Python slim image
FROM python:3.9-slim

# Install OpenSCAD and necessary dependencies
RUN apt-get update && apt-get install -y \
    openscad \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create the temp directory for renders
RUN mkdir -p temp_renders

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the application
CMD ["python", "server.py"]
