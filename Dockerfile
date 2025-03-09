FROM python:3.11-slim

# Install system dependencies required for xmlsec
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    pkg-config \
    xmlsec1 \
    postgresql \
    libpq-dev \
    build-essential \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*  # Clean up APT cache

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV XMLSEC_BINARY=/usr/bin/xmlsec1

# Create working directory
WORKDIR /app

# Copy requirements file first (for Docker cache optimization)
COPY requirements-shib.txt /app/

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --prefer-binary -r requirements-shib.txt

# Copy application files
COPY . /app/

# Ensure private keys and certificates are copied securely
COPY kulcs.crt /app/kulcs.crt
COPY kulcs.key /app/kulcs.key

# Expose port 3000
EXPOSE 3000

# Run application using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "saml_gunicorn:app"]
