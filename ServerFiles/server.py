"""
Remote sensing and processing server
Useful for receiving data coming in from remote sensors over the network
and live-plotting it.
CALIBRATION INFO:
ICE WATER mixed nicely gives 2.5/2.25 C
Boiling water gives: 99.25
NOTE: Very much EXPERIMENTAL!!
See Also
--------
client : a client that sends data to this.
"""

import socket
from queue import Queue
import threading
from threading import Thread
import time

import matplotlib.pyplot as plt
import matplotlib.animation as animation


SENSOR_TC = 0
SENSOR_INTERNAL = 1
SENSORS = {SENSOR_TC: 'Raspi1',
           SENSOR_INTERNAL: 'Time'}

stopEvent = threading.Event()


class Server(Thread):
    """
    Server to receive data from client sensors.

    Handles one or many clients
    """

    def __init__(self, dataQueue, config):
        self.kwargs = config["server"]

        self.SERVER_IP = self.kwargs["SERVER_IP"]
        self.TCP_PORT = self.kwargs["TCP_PORT"]
        self.BUFFER_SIZE = self.kwargs["BUFFER_SIZE"]

        Thread.__init__(self)
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind((self.SERVER_IP, self.TCP_PORT))
        self.serverSocket = serverSocket
        self.dataQueue = dataQueue
        self._stopped = False
        self._receivers = []

    def run(self):
        """
        Loop that listens for and processes client connections
        """
        print('Starting Server Thread')
        self.serverSocket.listen(1)
        while not stopEvent.isSet():
            # accept connections from outside
            clientSocket, address = self.serverSocket.accept()
            receiver = Receiver(clientSocket, address, self.dataQueue, self, self.BUFFER_SIZE)
            for d in receiver.run():
                yield d

    def close(self):
        self._stopped = True
        stopEvent.set()
        self.serverSocket.close()


class Receiver(Thread):
    """
    Get data from a single client
    """

    def __init__(self, clientSocket, address, dataQueue, server, BUFFER_SIZE):
        Thread.__init__(self)
        self.clientSocket = clientSocket
        self.address = address
        self.noDataCount = 0
        self.dataQueue = dataQueue
        self._stopped = False
        self._server = server
        self.BUFFER_SIZE = BUFFER_SIZE

    def run(self):
        # while not stopEvent.isSet():
        while True:
            # get data in possible buffer-sized chunks
            data = self.clientSocket.recv(self.BUFFER_SIZE)
            self.clientSocket.send(data)  # echo
            # print(f'data is {data}')
            yield data

    def stop(self):
        self._stopped = True
        self.close()
        self._server.close()
        stopEvent.set()

    def close(self):
        self.clientSocket.close()


# class ReceiverMultiSocket(Receiver):
#     """
#     One socket open/close per client communication.
#
#     This is inefficient and slows down when the data rate is high.
#     """
#
#     def run(self):
#         self.getOneDataPoint()
#
#     def postReceive(self):
#         self.close()


# class Plotter:
#     """
#     Plot window that updates as data becomes available
#     """
#
#     def __init__(self, temperatures):
#         # self.fig, self.ax = plt.subplots()
#         # self.lines = {}
#         # self.xdata, self.ydata = {}, {}
#         # for sensorID, sensorLabel in SENSORS.items():
#         #     line, = self.ax.plot([], [], lw=2, label=sensorLabel)
#         #     self.lines[sensorID] = line
#         #     self.xdata[sensorID], self.ydata[sensorID] = [], []
#         #
#         # self.ax.set_ylim(0, 30)
#         # self.ax.set_xlim(0, 50)
#         # self.ax.grid()
#         # plt.xlabel('Time (s)')
#         # plt.ylabel(r'Temperature ($^\circ$C)')
#         # plt.legend(loc='lower left')
#
#         self.temperatures = temperatures  # the Queue.
#         self._stopped = False
#
#     def stop(self):
#         self._stopped = True
#         stopEvent.set()
#
#     def getData(self):
#         """
#         Consume data in the thread-safe Queue as fast as it becomes available
#
#         This parses the data from the Queue. Multiple sensors, etc. could be handled
#         by putting a sensorID on the Queue tuples as well.
#         """
#         while not stopEvent.isSet():
#             if self._stopped:
#                 print("HJKHGJKHGJKLJHGJK")
#                 break
#             dataPoints = []
#             while not self.temperatures.empty() and not self._stopped:
#                 data = self.temperatures.get()
#                 if data and ',' in data:
#                     sensorID, timeVal, tempInC = data.split(',')
#                     sensorID = int(sensorID)
#                     timeVal = float(timeVal)
#                     tempInC = float(tempInC)
#                     if sensorID == -1:
#                         # end signaled
#                         self.stop()
#                     else:
#
#                         if sensorID == SENSOR_TC:
#                             print(tempInC)
#                         dataPoints.append((sensorID, timeVal, tempInC))
#             if dataPoints:
#                 yield dataPoints
#
#     # def addNewDataPoints(self, frameData):
#     #     """
#     #     update plot with new data point
#     #     """
#     #     for sensorID, dataTime, dataTemperature in frameData:
#     #         self.xdata[sensorID].append(dataTime)
#     #         self.ydata[sensorID].append(dataTemperature)
#     #         self._updateAxisLimits(dataTime, dataTemperature)
#     #         self.lines[sensorID].set_data(self.xdata[sensorID], self.ydata[sensorID])
#
#         # return self.lines[sensorID],
#
#     # def _updateAxisLimits(self, x, y):
#     #     """
#     #     Update axes if data goes out of bounds
#     #     """
#     #     ax = self.ax
#     #     xmin, xmax = ax.get_xlim()
#     #     ymin, ymax = ax.get_ylim()
#     #     if x >= xmax:
#     #         ax.set_xlim(xmin, 2 * xmax)
#     #         ax.figure.canvas.draw()
#     #     if x < xmin:
#     #         ax.set_xlim(0.9 * x, xmax)
#     #         ax.figure.canvas.draw()
#     #     if y >= ymax:
#     #         ax.set_ylim(ymin, 1.1 * ymax)
#     #         ax.figure.canvas.draw()
#     #     if y < ymin:
#     #         ax.set_ylim(y - 2, ymax)
#     #         ax.figure.canvas.draw()
#
#     def run(self):
#         print('Starting Plotting Thread')
#         while True:
#             print(self.getData)
#         # ani = animation.FuncAnimation(self.fig, self.addNewDataPoints, self.getData,
#         #                               blit=False, interval=100, repeat=False)
#         # plt.show()


class QueueMonitor(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self._stopped = False

    def run(self):
        while not self._stopped:
            time.sleep(10)
            print('Queue Length is {0}'.format(self.queue.qsize()))

    def stop(self):
        self._stopped = True
