FROM arm32v7/python:3.6.12-slim-buster

COPY dht22-logger.py ./

RUN apt update && apt install -y \
    build-essential

RUN python3 -m pip install --upgrade \
    pip \
    setuptools \
    wheel \
    pigpio \
    Adafruit_DHT \
    paho-mqtt


ENTRYPOINT ["python3", "dht22-logger.py"]
