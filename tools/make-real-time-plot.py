import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import threading
from datetime import datetime, timedelta


def main():
    mqtt_server_address = 'robert-kubica'
    topics_wildcards = ['plant/sensor/+/+', 'plant/+/+/status']
    mqtt_client = make_mqtt_client(mqtt_server_address, topics_wildcards)
    mqtt_client_thread = threading.Thread(target=mqtt_client_loop,
                                          args=(mqtt_client,)
                                          ).start()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator())
    plt.gcf().autofmt_xdate()

    x_axis_min = datetime.now() - timedelta(seconds=30)
    x_axis_max = datetime.now() + timedelta(seconds=30)
    plt.axis([x_axis_min, x_axis_max, 0, 100])
    plt.show()


def mqtt_client_loop(mqtt_client):
    while True:
        mqtt_client.loop()


def make_mqtt_client(mqtt_server_address, topics_wildcards):
    mqtt_client = mqtt.Client()
    try:
        print("Connecting to the MQTT broker at {}...".format(
            mqtt_server_address), end=' ')
        mqtt_client.connect(mqtt_server_address)
        print("connected.")
    except Exception as e:
        print("failed:", e)
        raise Exception('Connecting to the MQTT broker at {} failed: {}'.format(
            mqtt_server_address, e))

    for topic in topics_wildcards:
        mqtt_client.subscribe(topic)
        mqtt_client.message_callback_add(topic, on_message)

    return mqtt_client


def on_message(client, userdata, message):
    try:
        topic_parts = message.topic.split('/')
        device_type = topic_parts[1]
        device_id = topic_parts[2]
        message_subject = topic_parts[3]

        if device_type == 'sensor' and device_id == '1' and message_subject == 'temperature':
            print('device_type={}, device_id={}, message_subject={}'.format(
                device_type, device_id, message_subject))
            current_time = datetime.now().strftime('%H:%M:%S')
            data = float(message.payload.decode('utf-8'))

            x_axis_min = datetime.now() - timedelta(seconds=30)
            x_axis_max = datetime.now() + timedelta(seconds=30)
            plt.axis([x_axis_min, x_axis_max, 0, 100])

            print('{}, {}'.format(current_time, data))
            plt.scatter(data, current_time)
            plt.gcf().autofmt_xdate()

    except Exception as e:
        print('Something went wrong:\n\ttopic: {}\n\terror: {}'.format(
            message.topic, e))


if __name__ == "__main__":
    main()
