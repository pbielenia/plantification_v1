#!/usr/bin/python3

import os
import json
import paho.mqtt.client as mqtt
import sys


class ConfigProvider:
    def __init__(self, console_params, file_path):
        self.device_type = console_params[1]
        self.device_id = int(console_params[2])
        self.action = console_params[3]

        if self.action != 'on' and self.action != 'off':
            raise Exception('Unknown action: {}'.format(self.action))

        config_file = open(file_path, 'r')
        self._file_params = json.loads(config_file.read())

        self.control_topic = self._get_topic('controlTopic')

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


def print_usage():
    print('Usage: python3 {} <device-type> <device-id> <action:on|off>'
          .format(sys.argv[0]))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        if len(sys.argv) == 2 and sys.argv[1] == '--help':
            print_usage()
            exit(0)
        else:
            print_usage()
            exit(2)

    try:
        config_file_path = os.path.dirname(os.path.abspath(
            __file__)) + '/../mqtt-gpio-switcher/config.json'
        config_provider = ConfigProvider(sys.argv, config_file_path)

        message = None
        if config_provider.action == 'on':
            message = 'ENABLE'
        elif config_provider.action == 'off':
            message = 'DISABLE'

        mqtt_client = mqtt.Client()
        mqtt_client.connect('localhost')
        mqtt_client.publish(config_provider.control_topic, message)

        exit(0)

    except Exception as e:
        print('Something went wrong:\n\t', e)
        exit(1)
