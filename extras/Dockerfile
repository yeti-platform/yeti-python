FROM ubuntu:24.04

# Python
RUN apt-get update && apt-get install -y \
    python3-pip \
    libmagic-dev \
    git

# Upgrade pip
RUN pip3 install poetry --break-system-packages

COPY extras/docker-entrypoint.sh /docker-entrypoint.sh

# Mount app
ADD .. /app
WORKDIR /app
# RUN poetry install --no-root --with dev,plugins

ENV PYTHONPATH /app

ENTRYPOINT ["/bin/bash"]
