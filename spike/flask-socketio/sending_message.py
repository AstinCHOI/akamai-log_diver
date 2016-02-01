from flask import Flask, render_template
from flask_socketio import send, emit, SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('message')
def handle_message(message):
    send(message)

@socketio.on('json')
def handle_json(json):
    send(json, json=True)

# @socketio.on('my event')
# def handle_my_custom_event(json):
#     emit('my response', str(json))


# @socketio.on('message')
# def handle_message(message):
#     send(message, namespace='/chat')

# @socketio.on('my event')
# def handle_my_custom_event(json):
#     emit('my response', json, namespace='/chat')

# @socketio.on('my event')
# def handle_my_custom_event(json):
#     emit('my response', ('foo', 'bar', json), namespace='/chat')


def ack():
    print('message was received!')

@socketio.on('my event')
def handle_my_custom_event(json):
    emit('my response', str(json), callback=ack)


if __name__ == '__main__':
    socketio.run(app)