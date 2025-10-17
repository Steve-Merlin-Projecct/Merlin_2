# Use official Apify Python image with Playwright support
FROM apify/actor-python:3.11

# Set working directory
WORKDIR /usr/src/app

# Copy requirements first for better caching
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and system dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . ./

# Set up Python path
ENV PYTHONPATH=/usr/src/app

# Run the actor
CMD ["python", "actor_main.py"]
