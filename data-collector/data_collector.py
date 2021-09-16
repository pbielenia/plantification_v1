import paho.mqtt.client as mqtt
import re
import csv
import os
from datetime import datetime

SENSORS_TOPIC = "plant/sensor/+/+"
DEVICES_STATUS_TOPIC = "plant/+/+/status"


def run_data_collector():
    mqtt_client = mqtt.Client()
    mqtt_client.connect('localhost')

    mqtt_client.subscribe(SENSORS_TOPIC)
    mqtt_client.subscribe(DEVICES_STATUS_TOPIC)

    mqtt_client.message_callback_add(SENSORS_TOPIC, on_message)
    mqtt_client.message_callback_add(DEVICES_STATUS_TOPIC, on_message)

    if not os.path.exists('measures'):
        os.makedirs('measures')

    run = True
    while run:
        mqtt_client.loop()


def on_message(client, userdata, message):
    try:
        topic_regex_pattern = 'plant/.+/.+/.+'
        expected_topic_parts_len = len(topic_regex_pattern.split('/'))
        topic_parts = message.topic.split('/')

        if re.match(topic_regex_pattern, message.topic) is not None or len(topic_parts) == expected_topic_parts_len:
            device_type = topic_parts[1]
            device_id = topic_parts[2]
            file_path = None
            data = None

            if device_type == 'sensor':
                file_path, data = on_sensor_message(message)
            elif device_type == 'fan':
                file_path, data = on_device_message('fan', message)
            elif device_type == 'lamp':
                file_path, data = on_device_message('lamp', message)
            else:
                raise Exception("Unknown device type ({}) at topic {}".format(
                    device_type, message.topic))

            write_to_csv_file(file_path, device_type, device_id, data)

        else:
            print("Topic does not match the pattern: {}", message.topic)
            return

    except Exception as e:
        print('Something went wrong:\n\ttopic: {}\n\terror: {}'.format(
            message.topic, e))


def on_sensor_message(message):
    file_path = None
    data = None
    measured_quantity = message.topic.split('/')[3]

    if measured_quantity == 'temperature' or measured_quantity == 'humidity':
        file_path = 'measures/{}.csv'.format(measured_quantity)
        data = int(message.payload.decode('utf-8'))
    else:
        raise Exception(
            'Unknown measured quantity: {}'.format(measured_quantity))

    return file_path, data


def on_device_message(device, message):
    file_path = 'measures/{}.csv'.format(device)
    data = None
    status = message.payload.decode('utf-8').upper()

    if status == 'ENABLED':
        data = 1
    elif status == 'DISABLED':
        data = 0
    else:
        raise Exception('Unknown device status: {}'.format(status))

    return file_path, data


def write_to_csv_file(file, device_type, device_id, data):
    with open(file, 'a+', newline='') as csv_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_writer = csv.writer(csv_file, delimiter=',',
                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow([timestamp, device_type, device_id, data])


if __name__ == "__main__":
    run_data_collector()
