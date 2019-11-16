FROM alpine

WORKDIR /app
RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add --no-cache \
    python3 \
    py3-pip \
    openjdk11-jre \
    py3-numpy \
    py3-pandas@testing \
    gcc \
    python3-dev \
    musl-dev \
    py-numpy-dev \
    g++ \
    build-base
RUN pip3 install requests beautifulsoup4 google-api-python-client google-auth-httplib2 tabula-py
VOLUME [ "/app/config.py" ]
COPY . /app
CMD [ "python", "main.py" ]