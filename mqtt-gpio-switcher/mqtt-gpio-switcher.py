import paho.mqtt.client as mqtt
import pigpio
import json
import sys


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
        self._publish_status_message()

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
            self._publish_status_message()
        elif payload == self.control_disable_command:
            self._turn_pin_off()
            self._publish_status_message()
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


class ConfigProvider:
    def __init__(self, console_params, file_path):
        self.device_type = console_params[1]
        self.device_id = int(console_params[2])
        self.gpio_pin = int(console_params[3])

        config_file = open(file_path, 'r')
        self._file_params = json.loads(config_file.read())

        self.control_topic = self._get_topic('controlTopic')
        self.status_topic = self._get_topic('statusTopic')

    def _get_topic(self, json_key):
        device_type_placeholder = '<device-type>'
        device_id_placeholder = '<device-id>'

        if json_key in self._file_params:
            topic_scheme = self._file_params[json_key]
            if device_type_placeholder in topic_scheme and device_id_placeholder in topic_scheme:
                return topic_scheme.replace(
                    device_type_placeholder, self.device_type).replace(device_id_placeholder, str(self.device_id))
            else:
                raise Exception('Missing \"{}\" or \"{}\" placeholder in the topic scheme: \"{}\".'.format(
                    device_type_placeholder, device_id_placeholder, topic_scheme))
        else:
            raise Exception(
                'Key \"{}\" not found in the config file!'.format(json_key))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print('Usage: python3 {} <device-type> <device-id> <gpio-pin>'
              .format(sys.argv[0]))
        exit(2)

    try:
        config_provider = ConfigProvider(sys.argv, 'config.json')

        print('Startup parameters:\n'
              '\tgpio pin:', config_provider.gpio_pin, '\n'
              '\tcontrol topic:', config_provider.control_topic, '\n'
              '\tstatus topic:', config_provider.status_topic)

        with MqttGpioSwitcher(config_provider.gpio_pin,
                              config_provider.control_topic,
                              config_provider.status_topic) as mqtt_gpio_switcher:
            mqtt_gpio_switcher.start()

    except Exception as e:
        print('Something went wrong:\n\t', e)
        exit(1)
