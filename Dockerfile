FROM alpine:3.10

RUN \
	echo http://nl.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories && \
	apk update && \
	apk add \
	python3

RUN	apk add --virtual build-deps \
	coreutils \
	make \
	gcc \
	python3-dev \
	musl-dev \
	libffi-dev \
	openssl-dev

# PIP
RUN	pip3 install --no-cache-dir \
	requests \
	paho-mqtt \
	python-telegram-bot


# Cleaning up
RUN	apk del build-deps && \
	rm -rf /var/cache/apk/*

WORKDIR /app
VOLUME /app

CMD ["python3", "-u", "/app/main.py"]

