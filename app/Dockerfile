# Use AMD64 base image
FROM --platform=linux/amd64 python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy all files into the container
COPY . .

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Make sure input/output folders exist
RUN mkdir -p /app/input /app/output

# Set the entry point
CMD ["python", "main.py"]
