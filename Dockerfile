# Base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the required dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the run.sh file to the container
COPY run.sh .

# Set execute permissions for the run.sh file
RUN chmod +x run.sh

# Define the command to be executed when the container starts
CMD ["bash", "run.sh"]
