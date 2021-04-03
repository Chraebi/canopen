#!/usr/bin/python3
import canopen
import sys
import os
import traceback
import RPi.GPIO as GPIO
import time
from LEDHandler import LEDHandler
from timer import Timer

# Set up GPIO
GPIO.setmode(GPIO.BCM)  # Art der Pin-Nummerierung
GPIO.setup(5, GPIO.IN)  # Pin5 als digitalen Eingang festlegen, rauf
GPIO.setup(6, GPIO.IN)  # Pin6 als digitalen Eingang festlegen, runter
GPIO.setup(13, GPIO.IN)  # Pin13 als digitalen Eingang festlegen, Geschwindigkeit
GPIO.setup(19, GPIO.IN)  # Voltage enabled
GPIO.setup(20, GPIO.IN)  # Emergency Stop
# TODO add to separate file
os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ifconfig can0 up')
os.system('sudo ifconfig can0 txqueuelen 1000')
# set up global variables

led_handler = LEDHandler()

fast = False
velocity = 800
led_handler.orange.set_slow()


def check_voltage():
    # both on low if voltage is enabled (230V)
    voltage_enabled = GPIO.input(19) == 0
    emergency_stop_active = GPIO.input(20) == 1
    if emergency_stop_active:
        led_handler.red.set_fast()
        led_handler.green.set_off()
        return False
    led_handler.red.set_off()
    if not voltage_enabled:
        led_handler.green.set_slow()
        return False

    led_handler.green.set_on()
    return True


while not check_voltage():
    time.sleep(1)

try:
    # Start with creating a network representing one CAN bus
    network = canopen.Network()
    # Connect to the CAN bus
    network.connect(bustype='socketcan', channel='can0')
    network.check()
    # Add some nodes with corresponding Object Dictionaries
    node1 = canopen.BaseNode402(12, '/home/pi/canopen/examples/brunner_eds.eds')
    node2 = canopen.BaseNode402(15, '/home/pi/canopen/examples/brunner_eds.eds')
    for node in [node1, node2]:
        network.add_node(node)
        error_log = node.sdo[0x1003]
        for error in error_log.values():
            print("Error {0} was found in the log".format(error.raw))

        # Read a variable using SDO
        node.sdo[0x1006].raw = 1
        node.sdo[0x1014].raw = 163
        node.sdo[0x1003][0].raw = 0

    network.sync.start(0.1)
    for node in [node1, node2]:
        node.load_configuration()

        node.setup_402_state_machine()
        node.state = 'SWITCH ON DISABLED'

        node.op_mode = "PROFILED VELOCITY"
        # Read PDO configuration from node
        node.tpdo.read()
        # Re-map TxPDO1
        node.tpdo[1].clear()
        node.tpdo[1].add_variable('Statusword')
        node.tpdo[1].add_variable('Position actual value')
        node.tpdo[1].trans_type = 1
        node.tpdo[1].event_timer = 0
        node.tpdo[1].enabled = True
        # Save new PDO configuration to node
        node.tpdo.save()
        node.rpdo.read()
        node.state = 'READY TO SWITCH ON'


    def enable_operation():
        for node in [node1, node2]:
            timeout = time.time() + 15
            node.state = 'READY TO SWITCH ON'
            while node.state != 'READY TO SWITCH ON':
                if time.time() > timeout:
                    raise Exception('Timeout when trying to change state')
                time.sleep(0.001)

            timeout = time.time() + 15
            node.state = 'SWITCHED ON'
            while node.state != 'SWITCHED ON':
                if time.time() > timeout:
                    raise Exception('Timeout when trying to change state')
                time.sleep(0.001)

            timeout = time.time() + 15
            node.state = 'OPERATION ENABLED'
            while node.state != 'OPERATION ENABLED':
                if time.time() > timeout:
                    raise Exception('Timeout when trying to change state')
                time.sleep(0.001)


    def disable_operation():
        for node in [node1, node2]:
            timeout = time.time() + 15
            node.state = 'READY TO SWITCH ON'
            while node.state != 'READY TO SWITCH ON':
                if time.time() > timeout:
                    raise Exception('Timeout when trying to change state')
                time.sleep(0.001)
        led_handler.green.set_on()


    def up_vel(channel):
        global velocity
        node1.sdo[0x60FF].raw = velocity
        node2.sdo[0x60FF].raw = velocity


    def down_vel(channel):
        global velocity
        node1.sdo[0x60FF].raw = -velocity
        node2.sdo[0x60FF].raw = -velocity


    def stop(channel):
        node1.sdo[0x60FF].raw = 0
        node2.sdo[0x60FF].raw = 0


    def change_vel(channel):
        global fast
        global velocity
        if fast:
            velocity = 800
            fast = not fast
            led_handler.orange.set_slow()
        else:
            velocity = 1600
            fast = not fast
            led_handler.orange.set_fast()


    enable_operation()
    acceleration = 1600
    deceleration = acceleration
    node1.sdo[0x6083].raw = acceleration  # target acc
    node2.sdo[0x6083].raw = acceleration
    node1.sdo[0x6084].raw = deceleration  # target dec
    node2.sdo[0x6084].raw = deceleration

    GPIO.add_event_detect(13, GPIO.RISING, callback=change_vel, bouncetime=250)
    stop(None)
    timer = Timer(timeout=3)
    timer.start()
    while True:
        try:
            network.check()
        except Exception:
            break
        if check_voltage():
            if node1.state == 'OPERATION ENABLED' and node2.state == 'OPERATION ENABLED':
                up = GPIO.input(5)
                down = GPIO.input(6)
                if up == 0 and down == 1:
                    up_vel(channel=None)
                    timer.reset()
                elif down == 0 and up == 1:
                    down_vel(channel=None)
                    timer.reset()
                else:
                    stop(channel=None)
                if timer.is_expired():
                    disable_operation()
                time.sleep(0.01)
            else:
                up = GPIO.input(5)
                down = GPIO.input(6)
                if (up == 0 and down == 1) or (down == 0 and up == 1):
                    enable_operation()
        else:
            if node1.state == 'OPERATION ENABLED' and node2.state == 'OPERATION ENABLED':
                disable_operation()
            time.sleep(0.1)

except KeyboardInterrupt:
    pass

except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    traceback.print_exc()
    led_handler.red.set_fast()
    led_handler.green.set_fast()
    led_handler.orange.set_fast()

finally:
    global node1
    global node2
    global network
    # Disconnect from CAN bus
    print('going to exit... stopping...')
    node1.state = 'READY TO SWITCH ON'
    node2.state = 'READY TO SWITCH ON'
    node1.sdo[0x60FF].raw = 0
    node2.sdo[0x60FF].raw = 0
    # node.state = 'QUICK STOP ACTIVE'
    if network:
        for node_id in network:
            node = network[node_id]
            node.nmt.state = 'PRE-OPERATIONAL'
            node.nmt.stop_node_guarding()
        network.sync.stop()
        network.disconnect()
    GPIO.cleanup()
    os.system('sudo ifconfig can0 down')
