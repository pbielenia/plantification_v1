FROM arm32v7/python:3.6.12-slim-buster

RUN mkdir switch-gpio-state mqtt-gpio-switcher
COPY switch-gpio-state/switch-gpio-state.py ./switch-gpio-state/
COPY mqtt-gpio-switcher/config.json ./mqtt-gpio-switcher/

RUN apt update && apt install -y \
    build-essential

RUN python3 -m pip install --upgrade \
    pip \
    setuptools \
    wheel \
    paho-mqtt

ENTRYPOINT ["python3", "switch-gpio-state/switch-gpio-state.py"]
