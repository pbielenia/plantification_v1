import pigpio
import datetime 
import time
import enum
import sys
import signal
import paho.mqtt.client as mqtt


class FanDriver:
    def __init__(self, fan_id, gpio_pin):
        self.fan_id = fan_id
        self.gpio_pin = gpio_pin

        self.control_topic = 'plant/fan/{}/control'.format(fan_name)
        self.status_topic = 'plant/fan/{}/status'.format(fan_name)

        self.mqtt_client = mqtt.Client()
        self.pi = pigpio.pi()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.turn_fan_off()

    def start(self):
        self.mqtt_client.connect('localhost')
        self.mqtt_client.subscribe(self.control_topic)
        self.mqtt_client.message_callback_add(self.control_topic, self.on_control_topic_message)

        if not self.pi.connected:
            raise Exception('Cannot connect to GPIO')
        self.pi.set_mode(self.gpio_pin, pigpio.OUTPUT)
        self.turn_fan_off()

        run = True
        while run:
            self.mqtt_client.loop()

    def on_control_topic_message(self, client, userdata, message):
        payload = message.payload.decode('utf-8')
        if payload == 'ENABLE':
            self.turn_fan_on()
        elif payload == 'DISABLE':
            self.turn_fan_off()
        else:
            print('Unknown message:', payload)

    def turn_fan_on(self):
        self.pi.write(self.gpio_pin, 1)
        self.mqtt_client.publish(self.status_topic, 'ENABLED')

    def turn_fan_off(self):
        self.pi.write(self.gpio_pin, 0)
        self.mqtt_client.publish(self.status_topic, 'DISABLED')


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print('Usage: python3 fan-driver.py <name> <on/off pin>')
        exit(1)

    fan_name = sys.argv[1]
    gpio_pin = int(sys.argv[2])

    with FanDriver(fan_name, gpio_pin) as fan_driver:
        fan_driver.start()

