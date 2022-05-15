import numpy as np
from .server import GetData


def initSensor():
    data = GetData()
    print(data)
