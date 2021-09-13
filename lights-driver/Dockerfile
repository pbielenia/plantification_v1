FROM arm32v7/python:3.6.12-slim-buster

COPY lights-driver.py ./

RUN apt update && apt install -y \
    build-essential

RUN python3 -m pip install --upgrade \
    pip \
    setuptools \
    wheel \
    pigpio


ENTRYPOINT ["python3", "lights-driver.py"]
