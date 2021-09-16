import paho.mqtt.client as mqtt
import json
import re
import csv
import os

TEMPERATURE_TOPIC = "plant/temperature/sensor/+"
HUMIDITY_TOPIC = "plant/humidity/sensor/+"


def run_data_collector():
    mqtt_client = mqtt.Client()
    mqtt_client.connect('localhost')

    mqtt_client.subscribe(TEMPERATURE_TOPIC)
    mqtt_client.subscribe(HUMIDITY_TOPIC)

    mqtt_client.message_callback_add(TEMPERATURE_TOPIC, on_temperature_message)
    mqtt_client.message_callback_add(HUMIDITY_TOPIC, on_humidity_message)

    if not os.path.exists('measures'):
        os.makedirs('measures')

    run = True
    while run:
        mqtt_client.loop()


def on_temperature_message(client, userdata, message):
    topic_regex_pattern = "plant/temperature/sensor/.+"

    if re.match(topic_regex_pattern, message.topic) is not None:
        sensor_id = message.topic.split('/')[-1]

        data = json.loads(message.payload)
        temperature = data["temperature"]
        timestamp = data["timestamp"]

        print(
            "New measurement:\n  Topic:\t\t{}\n  Sensor ID:\t\t{}\n  Temperature:\t\t{}\n"
            "  Timestamp:\t\t{}\n".format(
                message.topic, sensor_id, temperature, timestamp))

        with open('measures/temperature.csv', 'a+', newline='') as csv_file:
            data_writer = csv.writer(csv_file, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data_writer.writerow([timestamp, sensor_id, temperature])


def on_humidity_message(client, userdata, message):
    topic_regex_pattern = "plant/humidity/sensor/.+"

    if re.match(topic_regex_pattern, message.topic) is not None:
        sensor_id = message.topic.split('/')[-1]

        data = json.loads(message.payload)
        humidity = data["humidity"]
        timestamp = data["timestamp"]

        print(
            "New measurement:\n  Topic:\t\t{}\n  Sensor ID:\t\t{}\n  Humidity:\t\t{}\n"
            "  Timestamp:\t\t{}\n".format(
                message.topic, sensor_id, humidity, timestamp))

        with open('measures/humidity.csv', 'a+', newline='') as csv_file:
            data_writer = csv.writer(csv_file, delimiter=',',
                                     quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data_writer.writerow([timestamp, sensor_id, humidity])


if __name__ == "__main__":
    run_data_collector()
