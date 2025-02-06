# Use the latest Python 3.13 image
FROM python:3.13

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django application files into the container
COPY . .

# Expose port 8000
EXPOSE 8000

# Run migrations and start the Django server
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
