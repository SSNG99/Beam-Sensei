# Dockerfile example:
FROM python:3.11.7

# Copy requirements.txt
COPY requirements.txt .

# Install needed Python packages
RUN pip install -r requirements.txt

# Copy the rest of the app's source code
COPY . .

# Set the command
CMD ["streamlit", "run", "new.py"]
