# https://hub.docker.com/_/python
FROM alpine:3.15

### 2. Get Java via the package manager
RUN apk update \
    && apk upgrade \
    && apk add --no-cache bash \
    && apk add --no-cache --virtual=build-dependencies unzip \
    && apk add --no-cache curl \
    && apk add --no-cache openjdk8-jre

### 3. Get Python, PIP

RUN apk add --no-cache python3 \
    && python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools \
    && rm -r /usr/lib/python*/ensurepip && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache
# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
WORKDIR /app

# Copy current directory into container at APP_HOME
COPY . /app

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

#### OPTIONAL : 4. SET JAVA_HOME environment variable, uncomment the line below if you need it

ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
