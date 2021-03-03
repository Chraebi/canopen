#!/usr/bin/python3
import RPi.GPIO as GPIO
import time

# Zaehler-Variable, global
Counter = 0
Tic = 0

GPIO.setmode(GPIO.BCM)  # Art der Pin-Nummerierung

GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # als digitalen Eingang festlegen
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # als digitalen Eingang festlegen
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # als digitalen Eingang festlegen
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # als digitalen Eingang festlegen
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # als digitalen Eingang festlegen
GPIO.setup(22, GPIO.OUT)  # als digitalen Ausgang festlegen
GPIO.setup(23, GPIO.OUT)  # als digitalen Ausgang festlegen
GPIO.setup(24, GPIO.OUT)  # als digitalen Ausgang festlegen

# Callback-Funktion
def Interrupt(channel):
  global Counter
  # Counter um eins erhoehen und ausgeben
  Counter = Counter + 1
  print("Counter " + str(Counter))
  print(channel)

# Interrupt-Event hinzufuegen, steigende Flanke
GPIO.add_event_detect(5, GPIO.RISING, callback = Interrupt, bouncetime = 250)
GPIO.add_event_detect(6, GPIO.RISING, callback = Interrupt, bouncetime = 250)
GPIO.add_event_detect(13, GPIO.RISING, callback = Interrupt, bouncetime = 250)
GPIO.add_event_detect(17, GPIO.RISING, callback = Interrupt, bouncetime = 250)
GPIO.add_event_detect(20, GPIO.RISING, callback = Interrupt, bouncetime = 250)

# Endlosschleife, bis Strg-C gedrueckt wird
try:
  while True:
    Tic = Tic + 1
    print("Tic %d" % Tic)
    time.sleep(1)
    if Tic % 2 == 0:
      GPIO.output(22, 1)
      GPIO.output(23, 1)
      GPIO.output(24, 1)
    elif Tic % 2 == 1:
      GPIO.output(22, 0)
      GPIO.output(23, 0)
      GPIO.output(24, 0)
except KeyboardInterrupt:
  GPIO.cleanup()
  print("\nBye")