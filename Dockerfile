# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY /src/app .
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Make sure you have a requirements.txt file with litestar and any other dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# For development purposes only
ENV CORS_ALLOW_ORIGIN="*"
ENV CONNECTION_STRING="sqlite+aiosqlite:///cq-datbase.sqlite"

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["litestar","run","--host","0.0.0.0","--debug"]