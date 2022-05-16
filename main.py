from ServerFiles import *
from ServerFiles import Server
import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation

config = {
    "server": {
        "SERVER_IP": "192.168.31.205",
        "TCP_PORT": 5500,
        "BUFFER_SIZE": 1024
    },
    "dt": 0.1,
    "P": 0.98
}

if __name__ == '__main__':

    Msg = Queue()
    KF = []
    data_init = []

    xs, cov = [], []

    velocity = np.zeros((1, 3))
    velocity_his = []

    p = np.array([[0, 0, 0]]).T
    position_his = []

    xs_data = []
    ys_data = []
    zs_data = []

    # try:
    server: Server = Server(Msg, config)
    for d in server.run():
        metaData = Convert(d)
        if len(data_init) <= 100:
            data_init.append(metaData)
        KF = data_var(data_init, config)
        if KF is not None:
            formedData, measuredData = data_format(metaData, config["dt"])
            KF.predict()
            KF.update(measuredData)

            filtered = np.dot(KF.H, KF.x)
            filtered[-1] -= 0.998

            xs.append(filtered)
            cov.append(KF.P)

            print(KF.P)

            velocity = zvu(xs[-1], velocity, config)
            velocity_his.append(velocity)

            p = position(p, velocity, filtered, config)

            xs_data.append(round(p[0][0], 3))
            ys_data.append(round(p[0][1], 3))
            zs_data.append(round(p[0][2], 3))

            ax = plt.axes(projection='3d')
            ax.plot3D(xs_data, ys_data, zs_data)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.set_zlabel('z');
            # plt.show()

            plt.pause(0.001)