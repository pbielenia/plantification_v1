FROM arm32v7/python:3.6.12-slim-buster

COPY mqtt-gpio-switcher.py .

RUN apt update && apt install -y \
    build-essential

RUN python3 -m pip install --upgrade \
    pip \
    setuptools \
    wheel \
    pigpio \
    paho-mqtt


ENTRYPOINT ["python3", "mqtt-gpio-switcher.py"]
