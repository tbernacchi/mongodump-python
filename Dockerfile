# Use the official Python base image
FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the Python script into the container
COPY requirements.txt script.py /app/

# Install any dependencies required by the script
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt && chmod a+rwx script.py

# Set the environment variable for the connection string
ENV DAYS ""
ENV HOST ""
ENV MONGO_PASS ""
ENV PROJECT ""

# Run the Python script when the container starts
CMD ["python3", "script.py"]
