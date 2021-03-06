# coding:UTF-8
# import serial
import time

ACCData = [0.0] * 8
GYROData = [0.0] * 8
mData = [0.0] * 8
FrameState = 0  # 通过\x后面的值判断属于哪一种情况
ByteNum = 0  # 读取到这一段的第几位
CheckSum = 0  # 求和校验位

a = [0.0] * 3
w = [0.0] * 3
m = [0.0] * 3


def DueData(inputData):  # 新增的核心程序，对读取的数据进行划分，各自读到对应的数组里
    global FrameState  # 在局部修改全局变量，要进行global的定义
    global ByteNum
    global CheckSum
    global a
    global w
    global m

    d = []
    for data in inputData:  # 在输入的数据进行遍历
        if FrameState == 0:  # 当未确定状态的时候，进入以下判断
            if data == 0x55 and ByteNum == 0:  # 0x55位于第一位时候，开始读取数据，增大ByteNum
                CheckSum = data
                ByteNum = 1
                continue
            elif data == 0x51 and ByteNum == 1:  # 在byte不为0 且 识别到 0x51 的时候，改变frame
                CheckSum += data
                FrameState = 1
                ByteNum = 2
            elif (data == 0x52) and (ByteNum == 1):  # 同理
                CheckSum += data
                FrameState = 2
                ByteNum = 2
            elif data == 0x54 and ByteNum == 1:
                CheckSum += data
                FrameState = 3
                ByteNum = 2

        elif FrameState == 1:  # acc    #已确定数据代表加速度
            if ByteNum < 10:  # 读取8个数据
                ACCData[ByteNum - 2] = data  # 从0开始
                CheckSum += data
                ByteNum += 1
            else:
                if data == (CheckSum & 0xff):  # 假如校验位正确
                    a = get_acc(ACCData)
                CheckSum = 0  # 各数据归零，进行新的循环判断
                ByteNum = 0
                FrameState = 0

        elif FrameState == 2:  # gyro
            if ByteNum < 10:
                GYROData[ByteNum - 2] = data
                CheckSum += data
                ByteNum += 1
            else:
                if data == (CheckSum & 0xff):
                    w = get_gyro(GYROData)
                CheckSum = 0
                ByteNum = 0
                FrameState = 0

        elif FrameState == 3:  # m
            if ByteNum < 10:
                mData[ByteNum - 2] = data
                CheckSum += data
                ByteNum += 1
            else:
                if data == (CheckSum & 0xff):
                    timeNow = time.time()
                    m = get_m(mData)
                    d = list(a) + list(w) + list(m)
                    d.append(timeNow)
                CheckSum = 0
                ByteNum = 0
                FrameState = 0

    if len(d) != 0:
        return d


def get_acc(datahex):
    axl = datahex[0]
    axh = datahex[1]
    ayl = datahex[2]
    ayh = datahex[3]
    azl = datahex[4]
    azh = datahex[5]

    k_acc = 16.0

    acc_x = (axh << 8 | axl) / 32768.0 * k_acc
    acc_y = (ayh << 8 | ayl) / 32768.0 * k_acc
    acc_z = (azh << 8 | azl) / 32768.0 * k_acc
    if acc_x >= k_acc:
        acc_x -= 2 * k_acc
    if acc_y >= k_acc:
        acc_y -= 2 * k_acc
    if acc_z >= k_acc:
        acc_z -= 2 * k_acc

    return acc_x, acc_y, acc_z


def get_gyro(datahex):
    wxl = datahex[0]
    wxh = datahex[1]
    wyl = datahex[2]
    wyh = datahex[3]
    wzl = datahex[4]
    wzh = datahex[5]
    k_gyro = 2000.0

    gyro_x = (wxh << 8 | wxl) / 32768.0 * k_gyro
    gyro_y = (wyh << 8 | wyl) / 32768.0 * k_gyro
    gyro_z = (wzh << 8 | wzl) / 32768.0 * k_gyro
    if gyro_x >= k_gyro:
        gyro_x -= 2 * k_gyro
    if gyro_y >= k_gyro:
        gyro_y -= 2 * k_gyro
    if gyro_z >= k_gyro:
        gyro_z -= 2 * k_gyro
    return gyro_x, gyro_y, gyro_z


def get_angle(datahex):
    rxl = datahex[0]
    rxh = datahex[1]
    ryl = datahex[2]
    ryh = datahex[3]
    rzl = datahex[4]
    rzh = datahex[5]
    k_angle = 180.0

    angle_x = (rxh << 8 | rxl) / 32768.0 * k_angle
    angle_y = (ryh << 8 | ryl) / 32768.0 * k_angle
    angle_z = (rzh << 8 | rzl) / 32768.0 * k_angle
    if angle_x >= k_angle:
        angle_x -= 2 * k_angle
    if angle_y >= k_angle:
        angle_y -= 2 * k_angle
    if angle_z >= k_angle:
        angle_z -= 2 * k_angle

    return angle_x, angle_y, angle_z


def get_m(datahex):
    hxl = datahex[0]
    hxh = datahex[1]
    hyl = datahex[2]
    hyh = datahex[3]
    hzl = datahex[4]
    hzh = datahex[5]

    k_m = 0.098

    m_x = ((hxh << 8) | hxl) * k_m
    m_y = ((hyh << 8) | hyl) * k_m
    m_z = ((hzh << 8) | hzl) * k_m

    unit = 300

    if m_x >= unit:
        m_x -= 2 * k_m
    if m_y >= unit:
        m_y -= 2 * k_m
    if m_z >= unit:
        m_z -= 2 * k_m

    return m_x, m_y, m_z

# def read_data():
#     ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)  # ser = serial.Serial('com7',115200, timeout=0.5)
#     print(ser.is_open)
#     while True:
#         datahex = ser.read(33)
#         DueData(datahex)

# if __name__ == "__main__":
#     ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)  # ser = serial.Serial('com7',115200, timeout=0.5)
#     print(ser.is_open)
#     while True:
#         datahex = ser.read(33)
#         for d in DueData(datahex):
#             print(f"a(g):{d[0]:.3f} {d[1]:.3f} {d[2]:.3f}\
#                   w(deg/s):{d[3]:.3f} {d[4]:.3f} {d[5]:.3f}\
#                   m(deg):{d[6]:.3f} {d[7]:.3f} {d[8]:.3f}"
