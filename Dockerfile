# Use an official lightweight Python image as the base
FROM python:3.11-slim

# Create a non-root user and set as default user
RUN useradd -m icalfixer

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

USER icalfixer

# Install Python dependencies (if you have a requirements.txt file)
# If you don't have additional dependencies, you can remove this line
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the server will run on
EXPOSE 8080

# Command to run the server
CMD ["python", "ical_fixer_server.py"]
