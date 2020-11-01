#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

# Zaehler-Variable, global
Counter = 0
Tic = 0

GPIO.setmode(GPIO.BCM)  # Art der Pin-Nummerierung

GPIO.setup(24, GPIO.IN)  # Pin24 als digitalen Eingang festlegen
GPIO.setup(22, GPIO.IN)  # Pin24 als digitalen Eingang festlegen
GPIO.setup(23, GPIO.IN)  # Pin24 als digitalen Eingang festlegen
# Callback-Funktion
def Interrupt(channel):
  global Counter
  # Counter um eins erhoehen und ausgeben
  Counter = Counter + 1
  print("Counter " + str(Counter))

# Interrupt-Event hinzufuegen, steigende Flanke
GPIO.add_event_detect(22, GPIO.RISING, callback = Interrupt, bouncetime = 250)
GPIO.add_event_detect(23, GPIO.RISING, callback = Interrupt, bouncetime = 250)
GPIO.add_event_detect(24, GPIO.RISING, callback = Interrupt, bouncetime = 250)

# Endlosschleife, bis Strg-C gedrueckt wird
try:
  while True:
    # nix Sinnvolles tun
    Tic = Tic + 1
    print("Tic %d" % Tic)
    time.sleep(1)
except KeyboardInterrupt:
  GPIO.cleanup()
  print("\nBye")