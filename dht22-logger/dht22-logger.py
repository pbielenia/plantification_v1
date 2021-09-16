#!/usr/bin/python3

import Adafruit_DHT
import json
import sys
import time
import paho.mqtt.client as mqtt

if __name__ == "__main__":
    # Intervals of about 2 seconds or less will eventually hang the DHT22.
    INTERVAL = 10

    DHT_SENSOR = Adafruit_DHT.DHT22
    dht_pin = int
    dht_id = int

    if len(sys.argv) != 3:
        print("Usage: python3 dht22-driver.py <sensor_pin> <sensor_id>")
        exit(1)
    else:
        dht_pin = sys.argv[1]
        dht_id = sys.argv[2]

    mqtt_client = mqtt.Client()
    print("Connecting to the local MQTT broker...", end=' ')
    mqtt_client.connect("localhost")
    print("connected.")

    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, dht_pin)

        if humidity is not None and temperature is not None:
            print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))

            timestamp = int(time.time())

            temperature_message = dict()
            temperature_message["temperature"] = round(temperature, 2)
            temperature_message["timestamp"] = timestamp

            humidity_message = dict()
            humidity_message["humidity"] = round(humidity, 2)
            humidity_message["timestamp"] = timestamp

            temperature_topic = "plant/temperature/sensor/{}".format(dht_id)
            mqtt_client.publish(temperature_topic,
                                payload=json.dumps(temperature_message))

            temperature_topic = "plant/humidity/sensor/{}".format(dht_id)
            mqtt_client.publish(temperature_topic,
                                payload=json.dumps(humidity_message))

        else:
            print("Failed to retrieve data from humidity sensor")

        time.sleep(2)
