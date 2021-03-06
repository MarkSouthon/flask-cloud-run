# Python image to use.
FROM python:3.10-slim

ENV PORT 80
ENV HOST 0.0.0.0

EXPOSE 80

# Install OpenJDK-17
RUN apt-get update && \
    apt-get install -y openjdk-17-jre && \
    apt-get clean;
    
ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64/
RUN export JAVA_HOME

# Copy local code to the container image.
WORKDIR /app

RUN pip install -U pip
# This upgrades pip to the newest available version.

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . /app

# Run report-check-app.py when the container launches
ENTRYPOINT ["python3"]

CMD ["report-check-app.py"]
