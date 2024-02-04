# Use an official Alpine Linux image with Python 3.8
FROM python:3.11-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apk add --no-cache gcc musl-dev linux-headers && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev linux-headers

# Run server.py when the container launches
CMD ["python", "./server.py"]