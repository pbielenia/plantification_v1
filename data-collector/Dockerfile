FROM arm32v7/python:3.6.12-slim-buster

WORKDIR /data_collector

COPY data_collector.py .

RUN apt update && apt install -y \
   build-essential

RUN python3 -m pip install --upgrade \
    pip \
    setuptools \
    wheel \
    paho-mqtt

ENTRYPOINT ["python3", "data_collector.py"]