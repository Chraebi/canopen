#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # Art der Pin-Nummerierung

GPIO.setup(24, GPIO.IN)  # Pin24 als digitalen Eingang festlegen
GPIO.setup(22, GPIO.IN)  # Pin24 als digitalen Eingang festlegen
GPIO.setup(23, GPIO.IN)  # Pin24 als digitalen Eingang festlegen

try:
    while True:  # Endlosschleife, mit Strg-C beenden
        input = GPIO.input(24)  # Eingang einlesen
        input1 = GPIO.input(22)  # Eingang einlesen
        input2 = GPIO.input(23)  # Eingang einlesen
        print("Zustand: " + str(input), "Zustand: " + str(input1), "Zustand: " + str(input2))  # Ausgabe auf Bildschirm
        time.sleep(0.1)  # kurze Pause
except KeyboardInterrupt:
    GPIO.cleanup()