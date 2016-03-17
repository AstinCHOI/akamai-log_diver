from gevent import monkey; monkey.patch_all()
from log_diver import socketio, application


if __name__ == "__main__":
    socketio.run()
