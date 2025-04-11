# Use Ubuntu-based Python 3.9 image
FROM python:3.9-slim-bullseye

# Set working directory
WORKDIR /app

# Install AWS CLI and required system packages
RUN apt-get update && \
    apt-get install -y \
    awscli \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script
COPY ec2_details_to_excel.py .

# Create directory for reports
RUN mkdir -p /app/ec2_reports

# Set the entry point
ENTRYPOINT ["python", "ec2_details_to_excel.py"] 