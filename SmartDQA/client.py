"""
Sensor client that sends sensor data to a server.
See Also
--------
server : the server.
"""

import socket
import time
import argparse


SPI_PORT = 0
SPI_DEVICE = 0
TCP_IP = None
TCP_PORT = 5500
BUFFER_SIZE = 1024

SENSOR_TC = 0
SENSOR_INTERNAL = 1


def senseTemperatures():
    # sensor = MAX31855.MAX31855(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
    timeStart = time.time()
    transmitter = TransmitterSingleSocket()
    try:
        while True:
            timeNow = time.time()
            timeVal = timeNow - timeStart
            # tempInC = sensor.readTempC()
            # internalTempInC = sensor.readInternalC()
            transmitter.sendDataPoint(timeVal)
            # transmitter.sendDataPoint(internalTempInC)
            time.sleep(0.05)
    except KeyboardInterrupt:
        transmitter.signalEnd()
        transmitter.close()


class Transmitter(object):

    def __init__(self):
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))

    def sendDataPoint(self, temperature):
        self.preSend()
        print(f'Send DATA is {temperature}!')
        self.socket.sendall(str.encode(f'Time interval {temperature}'))
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
    parser.add_argument('--serverip', default='127.0.0.1',
                        help='hostname or ip address of the server to connect to')

    args = parser.parse_args()
    TCP_IP = args.serverip
    senseTemperatures()
