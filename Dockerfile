# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Ensure the correct PATH
ENV PATH="/root/.local/bin:${PATH}"

# Expose the port Streamlit is running on (use 8080)
EXPOSE 8080

# Command to run the Streamlit app
CMD ["streamlit", "run", "your_script.py", "--server.port", "8080", "--server.headless", "true"]
