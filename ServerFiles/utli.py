import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise
from scipy.linalg import block_diag


def Convert(bits):
    string = bits.decode("utf-8")
    string = string[1:-1]
    li = list(string.split(", "))
    res = list(np.float_(li))
    return res


def data_var(data, config):
    if len(data) == 101:
        data = np.array(data)
        acc = data[:, 0:3]
        gyr = data[:, 3:6]
        accVar = np.var(acc, axis=0)
        gyoVar = np.var(gyr, axis=0)

        KF = initKF(accVar, gyoVar, config)
        return KF
    else:
        return None


def data_format(data, dt):
    """
    convert acceleration data to velocity

    :param data: acceleration data from sensor size is (1, 3)
    :param dt: sampling time interval
    :return: velocity and acceleration size is (1, 6)
    """

    data = np.array(data)
    accData = data[0:3]
    accData = accData[np.newaxis, :]
    xInput = np.zeros((1, 6))
    xInput[:, 0] = 0
    xInput[:, 1] = xInput[:, 0] + accData[:, 0] * dt

    xInput[:, 2] = 0
    xInput[:, 3] = xInput[:, 2] + accData[:, 1] * dt

    xInput[:, 4] = 0
    xInput[:, 5] = xInput[:, 4] + accData[:, 2] * dt

    return xInput.T, accData


def initKF(accVar, gyoVar, config):
    dt = config["dt"]
    P = config["P"]
    kf = KalmanFilter(dim_x=6, dim_z=3)

    dt = dt  # time step 0.1 second
    dt2 = dt * dt
    g = 9.96  # in m/s^2
    var_hdg = 0.005 ** 2
    var_ang_vel = gyoVar  # 0.002 ** 2
    var_acc = accVar  # (0.01 * g) ** 2

    # v_x =  v_x +  dt*a_x  +  0    +  0       +  0    +  0
    # a_x =   0  +  a_x     +  0    +  0       +  0    +  0
    # v_y =   0  +    0     +  v_y  +  dt*a_y  +  0    +  0
    # a_y =   0  +    0     +  0    +  a_y     +  0    +  0
    # v_z =   0  +    0     +  0    +  0       +  v_z  +  dt*a_z
    # a_z =   0  +    0     +  0    +  0       +  0    +  a_z

    kf.x = np.array([[0, 0, 0, 0, 0, 0]]).T  # initial state when bot starts from starting point. check
    # for theta (magnetometer measurement)
    if np.isscalar(P):
        kf.P *= P  # covariance matrix
    else:
        kf.P[:] = P  # [:] makes deep copy

    # F = np.array([[1, dt,  0,  0,  0,  0],
    #               [0,  1,  0,  0,  0,  0],
    #               [0,  0,  1, dt,  0,  0],
    #               [0,  0,  0,  1,  0,  0],
    #               [0,  0,  0,  0,  1, dt],
    #               [0,  0,  0,  0,  0,  1]])

    kf.F = np.array([[1, dt, 0, 0, 0, 0],
                     [0, 1, 0, 0, 0, 0],
                     [0, 0, 1, dt, 0, 0],
                     [0, 0, 0, 1, 0, 0],
                     [0, 0, 0, 0, 1, dt],
                     [0, 0, 0, 0, 0, 1]])

    q1 = Q_discrete_white_noise(dim=3, dt=dt, var=g * (0.1))  # In practice we pick a number, run simulations on
    # data, and choose a value that works well.
    q2 = block_diag(q1, q1)
    # q3 = Q_discrete_white_noise(dim=2, dt=dt, var=1)
    kf.Q = q2

    # x = [x_x, a_x, x_y, a_y, x_z, a_z].T   we only can get the a_x etc.
    # H = np.array([[0, 1, 0, 0,  0,  0],
    #               [0, 0, 0, 1,  0,  0],
    #               [0, 0, 0, 0,  0,  1]])

    kf.H = np.array([[0, 1, 0, 0, 0, 0],  # convert to the measurement space
                     [0, 0, 0, 1, 0, 0],
                     [0, 0, 0, 0, 0, 1]])

    kf.R = np.array([[var_acc[0], 0, 0],
                     [0, var_acc[1], 0],
                     [0, 0, var_acc[2]]])

    return kf


def zvu(filteredData, velocity, config):
    dt = config["dt"]
    a_threshold = 0.2
    v = velocity

    at = filteredData.T

    if np.linalg.norm(at) < a_threshold:
        v = np.zeros((3, 1))
    else:
        v = v + at * dt
    return v


def position(p, velocity, filteredData, config):
    dt = config["dt"]
    at = filteredData.T
    vt = velocity

    p = p + vt * dt + 0.5 * at * dt ** 2

    return p
