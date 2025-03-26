# Use an official lightweight Python runtime as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install required dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PORT=8080

# Expose the required port for Cloud Run
EXPOSE 8080

# Command to run the application
CMD ["python", "main.py"]
