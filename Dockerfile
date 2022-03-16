# Python image to use.
FROM python:3.10-slim

# Install OpenJDK-17
RUN apt-get update && \
    apt-get install -y openjdk-17-jre && \
    apt-get clean;

# Copy local code to the container image.
WORKDIR /app

RUN pip install -U pip
# This upgrades pip to the newest available version.

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Run app.py when the container launches
# ENTRYPOINT ["python", "report-check-app.py"]

# start uWSGI server
CMD ["uwsgi", "app.ini"]
