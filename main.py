from ServerFiles import *

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--serverip', default="192.168.31.205",
                        help='hostname or ip address of the server to connect to')

    args = parser.parse_args()
    SERVER_IP = args.serverip

    Msg = Queue()
    server, queueMonitor, plotter = (None, None, None)
    try:
        server = Server(Msg)
        server.start()
        plotter = Plotter(Msg)
        plotter.run()
    finally:
        if server:
            server.close()
        if plotter:
            plotter.stop()