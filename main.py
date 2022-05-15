from ServerFiles import *


config = {
    "server": {
        "SERVER_IP": "192.168.31.205",
        "TCP_PORT": 5500,
        "BUFFER_SIZE": 1024
    }
}

if __name__ == '__main__':

    Msg = Queue()
    server, queueMonitor, plotter = (None, None, None)

    try:
        server = Server(Msg, config)
        server.start()
        plotter = Plotter(Msg)
        plotter.run()
    finally:
        if server:
            server.close()
        if plotter:
            plotter.stop()