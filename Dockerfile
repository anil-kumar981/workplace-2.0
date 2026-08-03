# Python Image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file to the container
COPY req.txt .

# Install dependencies
RUN pip install --no-cache-dir -r req.txt

# Copy the entire project to container
COPY . .

# Expose the port
EXPOSE 8000

# Start fastapi server
CMD ["python", "main.py"]
