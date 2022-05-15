import serial
import argparse


def sensorSetting(reset=True, mf=False, settings=None):
    ser = serial.Serial("/dev/ttyS0", 9600, timeout=0.5)
    unlock = b'\xFF\xAA\x69\x88\xB5'  # 解锁
    ser.write(unlock)
    if reset:
        course_agl = b'\xFF\xAA\x01\x04\x00'  # 航向角归零
        ser.write(course_agl)
        alt = b'\xFF\xAA\x01\x03\x00'  # 高度归零
        ser.write(alt)
        acc = b'\xFF\xAA\x01\x01\x00'  # 自动加计归零
        ser.write(acc)
    if mf:
        # data = "\x FF\x AA\x 01\x 09\x 00"  # 磁场校准（双平面）
        # ser.write(data)
        data = b'\xFF\xAA\x01\x07x00'  # 磁场校准（球型拟合）
        ser.write(data)
    if settings is not None:
        ser.write(args.rate)  # sensor sampling rate

    save = b'\xFF\xAA\x00\xFF\x00'  # 保存设置
    ser.write(save)
    print(ser.readline())
    ser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--rate', default=b'\xFF\xAA\x03\x06\x00', help='sensor sampling rate at 10Hz')
    args = parser.parse_args()

    sensorSetting(settings=args)
