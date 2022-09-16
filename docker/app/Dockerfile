# Anystream server
#
# Build the image:  docker build -t semexp -f ./Dockerfile .
# Run the image:    docker run -p 8000:8000 semexp

FROM python:3.10.6-slim-buster

LABEL Name="app"
LABEL Description="Yogascape web app."
LABEL Vendor="Denis Kolokol"
LABEL Version="0.0.0.1"
LABEL Maintainer="admin@yogascape.org"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends\
	build-essential \
	gcc \
	git \
	openssh-server \
	python-dev \
	bash \
	&& rm -rf /var/lib/apt/lists/*

ENV WORKDIR /worker
RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR

# Avoid cache purge by adding requirements first
COPY app/requirements $WORKDIR/requirements

# Install dependencies
RUN pip install --upgrade pip \
	&& pip install -r requirements/live.txt --no-cache-dir

# Copy project files
COPY app $WORKDIR

# Expose port 8080
EXPOSE 8080

# copy && run entrypoint.sh
COPY docker/app/entrypoint.sh $WORKDIR
ENTRYPOINT ["/worker/entrypoint.sh"]
