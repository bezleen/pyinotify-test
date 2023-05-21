FROM python:3.8-slim-bullseye

RUN apt-get update \
    && apt-get install -y gcc vim supervisor procps \
    && apt-get install -y ffmpeg libsm6 libxext6 \
    && rm -rf /tmp/* /var/cache/* \
    && mkdir -p /var/log/apps


COPY . /webapps
WORKDIR /webapps

RUN pip install -r requirements.txt

ENTRYPOINT [ "tail", "-f", "/dev/null"]
