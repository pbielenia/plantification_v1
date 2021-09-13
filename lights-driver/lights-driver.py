import pigpio
import datetime 
import time
import enum

class LightsState(enum.Enum):
    TURNED_ON = enum.auto()
    TURNED_OFF = enum.auto()


class LightsDriver:
    def __init__(self, turn_on_time, turn_on_duration, pin):
        self.turn_on_time = turn_on_time
        self.turn_on_duration = turn_on_duration
        self.pin = pin

        print("----------------------")
        print("Lights pin number", self.pin)
        print("Turn on time:", self.turn_on_time)
        print("Turn on duration:", self.turn_on_duration, "hours")
        print("----------------------")

        self.current_state = LightsState.TURNED_OFF

        self.pi = pigpio.pi()

        if not self.pi.connected:
            raise Exception("Cannot connect to GPIO")
        
        self.pi.set_mode(self.pin, pigpio.OUTPUT)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.turn_lights_off()
        
    def __dummy_start(self):
        self.turn_lights_off()
        time.sleep(5)
        self.turn_lights_on()
        time.sleep(7 * 60 * 60)

        while True:
            self.turn_lights_off()
            time.sleep(12 * 60 * 60)
            self.turn_lights_on()
            time.sleep(12 * 60 * 60)

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
        today_lights_on_time = datetime.datetime.combine(current_time, self.turn_on_time)
        return today_lights_on_time <= current_time

    def turn_lights_on(self):
        print(datetime.datetime.now(), "Turning lights on...")
        self.pi.write(self.pin, 1)
        self.current_state = LightsState.TURNED_ON

    def turn_lights_off(self):
        print(datetime.datetime.now(), "Turning lights off...")
        self.pi.write(self.pin, 0)
        self.current_state = LightsState.TURNED_OFF

    def get_time_to_wait(self):
        if self.current_state == LightsState.TURNED_ON:
            today = datetime.datetime.today()
            destination = today.replace(day=today.day, hour=1) + datetime.timedelta(days=1)

if __name__ == "__main__":
    turn_on_time = datetime.time(20, 00)
    turn_on_duration = 6
    gpio_pin = 22

    with LightsDriver(turn_on_time, turn_on_duration, gpio_pin) as lights_driver:
        lights_driver.start()


