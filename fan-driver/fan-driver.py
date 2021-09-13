import pigpio
import datetime
import time
import enum
import sys
import signal
import paho.mqtt.client as mqtt


class FanDriver:
    def __init__(self, name, gpio_pin):
        self.name = name
        self.gpio_pin = gpio_pin

        self.control_topic = 'plant/fan/{}/control'.format(self.name)
        self.status_topic = 'plant/fan/{}/status'.format(self.name)

        self.control_enable_command = 'ENABLE'
        self.control_disable_command = 'DISABLE'

        self.mqtt_client = mqtt.Client()
        self.pi = pigpio.pi()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.turn_fan_off()

    def start(self):
        self.mqtt_client.connect('localhost')
        self.mqtt_client.subscribe(self.control_topic)
        self.mqtt_client.message_callback_add(
            self.control_topic, self.on_control_topic_message)

        if not self.pi.connected:
            raise Exception('Cannot connect to GPIO')

        self.pi.set_mode(self.gpio_pin, pigpio.OUTPUT)
        self.turn_fan_off()
        self.publish_pin_status()

        run = True
        while run:
            self.mqtt_client.loop()

    def on_control_topic_message(self, client, userdata, message):
        payload = message.payload.decode('utf-8')
        if payload == self.control_enable_command:
            self.turn_fan_on()
        elif payload == self.control_disable_command:
            self.turn_fan_off()
        else:
            print('Unknown message:', payload)
            self.publish_status_message(
                'Unknown message: {}. Available commands are: {}, {}.'
                .format(payload,
                        self.control_enable_command,
                        self.control_disable_command))

        self.publish_pin_status()

    def turn_fan_on(self):
        self.pi.write(self.gpio_pin, 1)

    def turn_fan_off(self):
        self.pi.write(self.gpio_pin, 0)

    def publish_status_message(self, message):
        self.mqtt_client.publish(self.status_topic, message)

    def publish_pin_status(self):
        pin_status = 'enabled' if self.pi.read(self.gpio_pin) else 'disabled'
        message = 'The fan on the pin {} has been {}.'.format(
            self.gpio_pin, pin_status)
        self.publish_status_message(message)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print('Usage: python3 fan-driver.py <fan-name> <gpio-pin>')
        exit(1)

    fan_name = sys.argv[1]
    gpio_pin = int(sys.argv[2])

    with FanDriver(fan_name, gpio_pin) as fan_driver:
        fan_driver.start()
