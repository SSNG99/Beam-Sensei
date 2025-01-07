# Dockerfile example:
FROM python:3.8-slim

# Working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install needed Python packages
RUN pip install -r requirements.txt

# Copy the rest of the app's source code
COPY . .

# Set the command
CMD ["streamlit", "run", "new.py"]
