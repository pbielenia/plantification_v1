import pigpio
import datetime
import time
import enum
import sys


class LightsState(enum.Enum):
    TURNED_ON = enum.auto()
    TURNED_OFF = enum.auto()


class LightsDriver:
    def __init__(self, gpio_pin, first_on_duration, turn_on_duration, turn_off_duration):
        self.gpio_pin = gpio_pin
        self.first_on_duration = first_on_duration
        self.turn_on_duration = turn_on_duration
        self.turn_off_duration = turn_off_duration

        self.current_state = LightsState.TURNED_OFF

        self.pi = pigpio.pi()

        if not self.pi.connected:
            raise Exception("Cannot connect to GPIO")

        self.pi.set_mode(self.gpio_pin, pigpio.OUTPUT)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.turn_lights_off()

    def __dummy_start(self):
        self.turn_lights_off()
        time.sleep(5)
        self.turn_lights_on()
        time.sleep(LightsDriver._hours_to_seconds(self.first_on_duration))

        while True:
            self.turn_lights_off()
            time.sleep(LightsDriver._hours_to_seconds(self.turn_off_duration))
            self.turn_lights_on()
            time.sleep(LightsDriver._hours_to_seconds(self.turn_on_duration))

    def _hours_to_seconds(hours):
        return hours * 60 * 60

    def start(self):
        self.__dummy_start()
        return

        if self.lights_should_be_turned_on():
            self.turn_lights_on()
        else:
            self.turn_lights_off()

        waiting_time = self.get_time_to_wait()

        print("Going to sleep...")
        time.sleep(2000)

    def lights_should_be_turned_on(self):
        current_time = datetime.datetime.today()
        today_lights_on_time = datetime.datetime.combine(
            current_time, self.turn_on_time)
        return today_lights_on_time <= current_time

    def turn_lights_on(self):
        print(datetime.datetime.now(), "Turning lights on...")
        self.pi.write(self.gpio_pin, 1)
        self.current_state = LightsState.TURNED_ON

    def turn_lights_off(self):
        print(datetime.datetime.now(), "Turning lights off...")
        self.pi.write(self.gpio_pin, 0)
        self.current_state = LightsState.TURNED_OFF

    def get_time_to_wait(self):
        if self.current_state == LightsState.TURNED_ON:
            today = datetime.datetime.today()
            destination = today.replace(
                day=today.day, hour=1) + datetime.timedelta(days=1)


if __name__ == "__main__":

    if len(sys.argv) != 5:
        print(
            'Usage: python3 {} <gpio-pin> <time-shift> <turn-on-duration> <turn-off-duration>' .format(sys.argv[0]))
        exit(1)

    gpio_pin = int(sys.argv[1])
    first_on_duration = int(sys.argv[2])
    turn_on_duration = int(sys.argv[3])
    turn_off_duration = int(sys.argv[4])

    with LightsDriver(gpio_pin, first_on_duration, turn_on_duration, turn_off_duration) as lights_driver:
        lights_driver.start()
