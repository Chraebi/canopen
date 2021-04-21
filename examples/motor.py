#!/usr/bin/python3
import canopen
import os
import time


class Motor:
    def __init__(self):
        # set up global variables
        self.velocity = 800
        self.fast = False
        self.network = None
        self.node1 = None
        self.node2 = None
        self.is_setup = False

    def setup(self):
        try:
            os.system('sudo ip link set can0 type can bitrate 1000000')
            os.system('sudo ifconfig can0 up')
            os.system('sudo ifconfig can0 txqueuelen 1000')
            # Start with creating a network representing one CAN bus
            self.network = canopen.Network()
            # Connect to the CAN bus
            self.network.connect(bustype='socketcan', channel='can0')
            self.network.check()
            # Add some nodes with corresponding Object Dictionaries
            self.node1 = canopen.BaseNode402(12, '/home/pi/canopen/examples/brunner_eds.eds')
            self.node2 = canopen.BaseNode402(15, '/home/pi/canopen/examples/brunner_eds.eds')
            for node in [self.node1, self.node2]:
                self.network.add_node(node)
                # Read a variable using SDO
                node.sdo[0x1006].raw = 1
                node.sdo[0x1014].raw = 163
                node.sdo[0x1003][0].raw = 0
                # Transmit SYNC every 100 ms

            self.network.sync.start(0.1)
            for node in [self.node1, self.node2]:
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

            acceleration = 1600
            deceleration = acceleration
            self.node1.sdo[0x6083].raw = acceleration  # target acc
            self.node2.sdo[0x6083].raw = acceleration
            self.node1.sdo[0x6084].raw = deceleration  # target dec
            self.node2.sdo[0x6084].raw = deceleration
            self.is_setup = True
        except Exception as e:
            self.is_setup = False

    def enable_operation(self):
        for node in [self.node1, self.node2]:
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

    def disable_operation(self):
        for node in [self.node1, self.node2]:
            timeout = time.time() + 15
            node.state = 'READY TO SWITCH ON'
            while node.state != 'READY TO SWITCH ON':
                if time.time() > timeout:
                    raise Exception('Timeout when trying to change state')
                time.sleep(0.001)

    def up_vel(self):
        self.node1.sdo[0x60FF].raw = self.velocity
        self.node2.sdo[0x60FF].raw = self.velocity

    def down_vel(self):
        self.node1.sdo[0x60FF].raw = -self.velocity
        self.node2.sdo[0x60FF].raw = -self.velocity

    def stop(self):
        self.node1.sdo[0x60FF].raw = 0
        self.node2.sdo[0x60FF].raw = 0

    def change_vel(self):
        if self.fast:
            self.velocity = 800
            self.fast = False
        else:
            self.velocity = 1600
            self.fast = True

    def clean_up(self):
        self.__init__()
        os.system('sudo ifconfig can0 down')
