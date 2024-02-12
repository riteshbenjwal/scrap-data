# Use an official Python runtime as a parent image
FROM python:3.8-alpine

# Set the working directory in the container
WORKDIR /usr/src

COPY ./requirements.txt /usr/src/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

# Copy the current directory contents into the container at /usr/src/
COPY ./app /usr/src/app


# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
