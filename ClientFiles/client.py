"""
Sensor client that sends sensor data to a server.
See Also
--------
server : the server.
"""

import socket
import argparse
import serial
from witSensor import *

SPI_PORT = 0
SPI_DEVICE = 0
TCP_IP = None
TCP_PORT = 5500
BUFFER_SIZE = 1024

SENSOR_TC = 0
SENSOR_INTERNAL = 1


def senseTemperatures():  # TO DO rename it to sensorInit
    ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)  # ser = serial.Serial('com7',115200, timeout=0.5)
    print(ser.is_open)

    transmitter = TransmitterSingleSocket()
    try:
        while True:
            dataHex = ser.read(33)
            data = DueData(dataHex)
            if data is not None:
                transmitter.sendDataPoint(data)

    except KeyboardInterrupt:
        transmitter.signalEnd()
        transmitter.close()


class Transmitter(object):

    def __init__(self):
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))

    def sendDataPoint(self, transmitData):
        self.preSend()
        # print(f'Send DATA is {transmitData}')
        self.socket.sendall(str.encode(str(transmitData)))
        data = self.socket.recv(BUFFER_SIZE)
        self.postSend()

    def signalEnd(self):
        self.sendDataPoint(-1, 0, 0)

    def close(self):
        self.socket.close()

    def preSend(self):
        pass

    def postSend(self):
        pass


class TransmitterSingleSocket(Transmitter):
    def __init__(self):
        Transmitter.__init__(self)
        self.connect()


class TransmitterMultiSocket(Transmitter):

    def preSend(self):
        self.connect()

    def postSend(self):
        self.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--serverip', default='192.168.31.205',
                        help='hostname or ip address of the server to connect to')

    args = parser.parse_args()
    TCP_IP = args.serverip
    senseTemperatures()
