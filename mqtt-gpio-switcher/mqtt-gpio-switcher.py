import pigpio
import sys
import paho.mqtt.client as mqtt


class MqttGpioSwitcher:
    def __init__(self, gpio_pin, control_topic, status_topic):
        self.gpio_pin = gpio_pin
        self.control_topic = control_topic
        self.status_topic = status_topic

        self.control_enable_command = 'ENABLE'
        self.control_disable_command = 'DISABLE'

        self._mqtt_client = mqtt.Client()
        self._gpio = pigpio.pi()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._turn_pin_off()

    def start(self):
        self._init_mqtt_client()
        self._init_pigpio()

        self._turn_pin_off()
        self._publish_status_message()

        self._enter_mqtt_loop()

    def _init_mqtt_client(self):
        self._mqtt_client.connect('localhost')
        self._mqtt_client.subscribe(self.control_topic)
        self._mqtt_client.message_callback_add(
            self.control_topic, self.on_control_topic_message)

    def _init_pigpio(self):
        if not self._gpio.connected:
            raise Exception('Cannot connect to GPIO')
        self._gpio.set_mode(self.gpio_pin, pigpio.OUTPUT)

    def on_control_topic_message(self, client, userdata, message):
        payload = message.payload.decode('utf-8').upper()
        if payload == self.control_enable_command:
            self._turn_pin_on()
            self._publish_pin_status()
        elif payload == self.control_disable_command:
            self._turn_pin_off()
            self._publish_pin_status()
        else:
            print('Unknown message: {}. Available commands are: {}, {}.'
                  .format(payload,
                          self.control_enable_command,
                          self.control_disable_command))

    def _turn_pin_on(self):
        self._gpio.write(self.gpio_pin, 1)

    def _turn_pin_off(self):
        self._gpio.write(self.gpio_pin, 0)

    def _publish_status_message(self):
        message = 'enabled' if self._gpio.read(self.gpio_pin) else 'disabled'
        self._mqtt_client.publish(self.status_topic, message)

    def _enter_mqtt_loop(self):
        run = True
        while run:
            self._mqtt_client.loop()


if __name__ == "__main__":

    if len(sys.argv) != 4:
        print('Usage: python3 {} <device-type> <device-id> <gpio-pin>'
              .format(sys.argv[0]))
        exit(1)

    device_type = sys.argv[1]
    device_id = int(sys.argv[2])
    gpio_pin = int(sys.argv[3])

    # todo: validate inputs
    # todo: read topics schemes from json

    control_topic = "plant/{}/{}/control".format(device_type, device_id)
    status_topic = "plant/{}/{}/status".format(device_type, device_id)

    with MqttGpioSwitcher(gpio_pin, control_topic, status_topic) as mqtt_gpio_switcher:
        mqtt_gpio_switcher.start()
