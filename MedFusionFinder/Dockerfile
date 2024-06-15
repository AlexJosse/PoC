# Use a base image with transformers pre-installed
FROM huggingface/transformers-pytorch-cpu:latest

# Set environment variables for locale
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the application code into the container
COPY . .

# Create a directory for uploaded files and set permissions
RUN mkdir -p /app/uploads && chmod -R 777 /app/uploads

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port 5000 to the host
EXPOSE 5000

# Command to run the Flask application
CMD ["flask", "run"]




