#!/usr/bin/python3

import Adafruit_DHT
import paho.mqtt.client as mqtt
import sys
import time

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

    temperature_topic = "plant/sensor/{}/temperature".format(dht_id)
    humidity_topic = "plant/sensor/{}/humidity".format(dht_id)

    while True:
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, dht_pin)

        if humidity is not None and temperature is not None:
            print(
                "Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))

            temperature_message = round(temperature, 2)
            humidity_message = round(humidity, 2)

            mqtt_client.publish(temperature_topic, payload=temperature_message)
            mqtt_client.publish(humidity_topic, payload=humidity_message)

        else:
            print("Failed to retrieve data from humidity sensor")

        time.sleep(INTERVAL)
