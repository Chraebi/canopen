#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
from LEDHandler import LEDHandler
from motor import Motor
from timer import Timer


def check_voltage():
    return GPIO.input(19) == 0


def emergency_enabled():
    return GPIO.input(20) == 1


def change_vel(channel):
    if not lift.fast:
        led_handler.orange.set_fast()
    else:
        led_handler.orange.set_slow()
    lift.change_vel()


if __name__ == "__main__":
    # Set up GPIO
    GPIO.setmode(GPIO.BCM)  # Type of numeration
    GPIO.setup(5, GPIO.IN)  # upwards
    GPIO.setup(6, GPIO.IN)  # downwards
    GPIO.setup(13, GPIO.IN)  # velocity
    GPIO.setup(19, GPIO.IN)  # Voltage enabled
    GPIO.setup(20, GPIO.IN)  # Emergency Stop
    GPIO.add_event_detect(13, GPIO.RISING, callback=change_vel, bouncetime=250)
    led_handler = LEDHandler()
    lift = Motor()
    timer = Timer(timeout=2)
    led_timer = Timer(timeout=120)
    led_timer.start()
    timer.start()
    while True:
        if emergency_enabled():
            if led_timer.is_expired():
                led_handler.orange.set_off()
                led_handler.green.set_off()
                led_handler.red.set_off()
            else:
                led_handler.red.set_slow()
                led_handler.orange.set_off()
                led_handler.green.set_off()
            continue
        else:
            led_timer.reset()
            led_handler.red.set_off()
        if not check_voltage():
            led_handler.green.set_slow()
            lift.clean_up()
            time.sleep(1)
            continue
        if not lift.is_setup:
            time.sleep(1)
            lift.setup()
            led_handler.green.set_on()
            continue
        if not lift.fast:
            led_handler.orange.set_slow()
        else:
            led_handler.orange.set_fast()
        if lift.node1.state == 'OPERATION ENABLED' and lift.node2.state == 'OPERATION ENABLED':
            up = GPIO.input(5)
            down = GPIO.input(6)
            if up == 0 and down == 1:
                lift.up_vel()
                timer.reset()
            elif down == 0 and up == 1:
                lift.down_vel()
                timer.reset()
            else:
                lift.stop()
            if timer.is_expired():
                lift.disable_operation()
            time.sleep(0.01)
        else:
            up = GPIO.input(5)
            down = GPIO.input(6)
            if (up == 0 and down == 1) or (down == 0 and up == 1):
                lift.enable_operation()
        time.sleep(0.1)
