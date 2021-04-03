#!/usr/bin/python3
from time import sleep
from threading import Thread, Lock
import RPi.GPIO as GPIO


class LEDHandler:
    def __init__(self):
        self.orange = LED(22)
        self.green = LED(23)
        self.red = LED(24)
        self.LEDS = [self.green, self.orange, self.red]
        for x in self.LEDS:
            GPIO.setup(x.channel, GPIO.OUT)
            GPIO.output(x.channel, 1)
        blinking_thread = Thread(target=self.blinking)
        blinking_thread.start()

    def blinking(self):
        while True:

            ''''
            --__
            _-_-
            ____
            ----
            '''
            for x in self.LEDS:
                if x.fast or x.slow or x.on:
                    GPIO.output(x.channel, 0)
            sleep(0.5)
            for x in self.LEDS:
                if x.fast or x.off:
                    GPIO.output(x.channel, 1)
            sleep(0.5)
            for x in self.LEDS:
                if x.fast or x.slow or x.on:
                    GPIO.output(x.channel, 0)
            sleep(0.5)
            for x in self.LEDS:
                if x.fast or x.off or x.slow:
                    GPIO.output(x.channel, 1)
            sleep(0.5)


class LED:
    def __init__(self, channel):
        self._lock = Lock()
        self.channel = channel
        self.fast = False
        self.slow = False
        self.on = False
        self.off = False

    def set_off(self):
        with self._lock:
            self.off = True
            self.fast = False
            self.slow = False
            self.on = False

    def set_slow(self):
        with self._lock:
            self.slow = True
            self.off = False
            self.fast = False
            self.on = False

    def set_fast(self):
        with self._lock:
            self.fast = True
            self.off = False
            self.slow = False
            self.on = False

    def set_on(self):
        with self._lock:
            self.on = True
            self.off = False
            self.fast = False
            self.slow = False
