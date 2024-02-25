# Use an official Python runtime as a parent image
FROM python:3.11.4-slim

# Set the working directory in the container
WORKDIR /api

# Copy the current directory contents into workdir
COPY . /api

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE ${FLASK_API_PORT}

# Run api.py when the container launches
CMD ["flask", "run", "--port=8001"]
