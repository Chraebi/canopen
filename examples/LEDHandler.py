#!/usr/bin/python3
from time import sleep
from threading import Thread, Event
import RPi.GPIO as GPIO


class LEDHandler():
    def __init__(self):
        self.fast = Event()
        self.ready = Event()
        self.error = Event()
        self.orange = 22
        self.green = 23
        self.red = 24
        vel_thread = Thread(target=self.velocity_handler)
        mode_thread = Thread(target=self.mode_handler)
        error_thread = Thread(target=self.error_handler)
        vel_thread.start()
        mode_thread.start()
        error_thread.start()

    def velocity_handler(self):
        GPIO.setup(self.orange, GPIO.OUT)  # Pin22 als digitalen Ausgang festlegen, LED orange, Geschwindigkeit
        on = True
        GPIO.output(self.orange, 0)

        while True:
            time_out = 0.5 if self.fast.isSet() else 1
            if on:
                GPIO.output(self.orange, 0)
            else:
                GPIO.output(self.orange, 1)
            on = not on
            sleep(time_out)

    def mode_handler(self):
        GPIO.setup(self.green, GPIO.OUT)  # Pin23 als digitalen Ausgang festlegen, LED grün
        GPIO.output(self.green, 1)
        while True:
            if self.ready.isSet():
                GPIO.output(self.green, 0)
            else:
                GPIO.output(self.green, 1)
            sleep(0.2)

    def error_handler(self):
        GPIO.setup(self.red, GPIO.OUT)  # Pin23 als digitalen Ausgang festlegen, LED rot
        GPIO.output(self.red, 1)
        while True:
            if self.error.isSet():
                GPIO.output(self.red, 0)
            else:
                GPIO.output(self.red, 1)
            sleep(0.2)