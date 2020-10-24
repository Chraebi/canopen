import canopen
import sys
import os
import traceback

import time

# TODO add to separate file
os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ifconfig can0 up')
os.system('sudo ifconfig can0 txqueuelen 1000')
try:

    # Start with creating a network representing one CAN bus
    network = canopen.Network()

    # Connect to the CAN bus
    network.connect(bustype='socketcan', channel='can0')

    network.check()

    # Add some nodes with corresponding Object Dictionaries
    # node = canopen.BaseNode402(12, 'sample.eds')
    node1 = canopen.BaseNode402(12, 'brunner_eds.eds')
    node2 = canopen.BaseNode402(15, 'brunner_eds.eds')
    for node in [node1, node2]:
        network.add_node(node)

        # Reset network, change states
        node.nmt.state = 'RESET COMMUNICATION'
        node.nmt.state = 'RESET'
        node.nmt.wait_for_bootup(15)

        print('node state 1) = {0}'.format(node.nmt.state))

        # Iterate over arrays or records
        # TODO: Test an error
        error_log = node.sdo[0x1003]
        for error in error_log.values():
            print("Error {0} was found in the log".format(error.raw))

        for node_id in network:
            print(network[node_id])

        print('node state 2) = {0}'.format(node.nmt.state))

        # Read a variable using SDO
        node.sdo[0x1006].raw = 1
        # node.sdo[0x100c].raw = 100
        # node.sdo[0x100d].raw = 3
        node.sdo[0x1014].raw = 163
        node.sdo[0x1003][0].raw = 0
        # exit(0)
        # Transmit SYNC every 100 ms

    network.sync.start(0.1)
    print("Sync start")
    for node in [node1, node2]:
        node.load_configuration()
        # exit(1)
        print('node state 3) = {0}'.format(node.nmt.state))

        node.setup_402_state_machine()

        device_name = node.sdo[0x1008].raw
        vendor_id = node.sdo[0x1018][1].raw
        velocity_target = node.sdo[0x1009].raw
        velocity = node.sdo[0x60FF].raw
        position = node.sdo[0x607A].raw
        target_vel = node.sdo[0x6081].raw
        supported_mode = node.sdo[0x6502].raw
        motion_profile = node.sdo[0x6086].raw
        print("-----------------------------------")
        node.sdo[0x607A].raw = 2000000  # Target Post
        node.state = 'SWITCH ON DISABLED'

        print('node state 4) = {0}'.format(node.nmt.state))
        node.op_mode = "PROFILED VELOCITY"
        # node.op_mode = "PROFILED POSITION"
        # Read PDO configuration from node
        node.tpdo.read()
        # Re-map TxPDO1
        node.tpdo[1].clear()
        node.tpdo[1].add_variable('Statusword')
        # node.tpdo[1].add_variable('Velocity actual value')
        node.tpdo[1].add_variable('Position actual value')
        node.tpdo[1].trans_type = 1
        node.tpdo[1].event_timer = 0
        node.tpdo[1].enabled = True
        # Save new PDO configuration to node
        node.tpdo.save()
        # publish the a value to the control word (in this case reset the fault at the motors)

        node.rpdo.read()
        # node.rpdo[1]['Controlword'].raw = 0x80
        # node.rpdo[1].transmit()
        # node.rpdo[1]['Controlword'].raw = 0x81
        # node.rpdo[1].transmit()

        node.state = 'READY TO SWITCH ON'
        node.state = 'SWITCHED ON'

        # node.rpdo.export('database.dbc')

        # -----------------------------------------------------------------------------------------

        print('Node booted up')

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

    # print('Node Status {0}'.format(node.powerstate_402.state))

    # -----------------------------------------------------------------------------------------
    #node1.nmt.start_node_guarding(0.01)
    #node.nmt.start_node_guarding(0.01)
    #
    node1.sdo[0x6086].raw = 1
    node2.sdo[0x6086].raw = 1
    node1.sdo[0x6081].raw = 500
    node2.sdo[0x6081].raw = 500
    node1.sdo[0x60FF].raw = 800
    node2.sdo[0x60FF].raw = 800
    # node.sdo[0x607A].raw = 2000000 # Target Post
    while True:
        try:
            network.check()
        except Exception:
            break

        # Read a value from TxPDO1
        #node.tpdo[1].wait_for_reception()
        # speed = node.tpdo[1]['Velocity actual value'].phys
        #position = node.tpdo[1]['Position actual value'].phys

        # Read the state of the Statusword
        #statusword = node.sdo[0x6041].raw

        #print('statusword: {0}'.format(statusword))
        #print('VEL: {0}'.format(position))
        #print(node.op_mode)
        time.sleep(0.01)

except KeyboardInterrupt:
    pass
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    traceback.print_exc()
finally:
    # Disconnect from CAN bus
    print('going to exit... stopping...')
    node1.state = 'READY TO SWITCH ON'
    node2.state = 'READY TO SWITCH ON'
    # node.state = 'QUICK STOP ACTIVE'
    if network:
        for node_id in network:
            node = network[node_id]
            node.nmt.state = 'PRE-OPERATIONAL'
            node.nmt.stop_node_guarding()
        network.sync.stop()
        network.disconnect()

    os.system('sudo ifconfig can0 down')
