from flask import Flask, render_template_string
from flask_socketio import SocketIO
import capture

app = Flask(__name__)
app.secret_key = 'your secret here'
sio = SocketIO(app)

@app.route("/")
def hello_world():
    screen_data = capture.grabScreen(new_session=True)
    hstr = ""
    with open("home.html", "r") as html:
        hstr = html.read()

    return render_template_string(
        hstr, 
        width=capture.SCREEN_ROW, 
        height=capture.SCREEN_COL,
        data=screen_data
    )

from threading import Lock
thread = None
thread_lock = Lock()

def background_task():
    while True:
        sio.sleep(0.1)
        screen_data = capture.grabScreen()
        if screen_data:
            sio.emit('image_change', {'data': screen_data })

@sio.on('connect')
def connect():
    print("Connected")
    screen_data = capture.grabScreen(new_session=True)
    if screen_data:
        sio.emit('image_change', {'data': screen_data })
    global thread
    with thread_lock:
        if thread is None:
            thread = sio.start_background_task(background_task)

@sio.on('disconnect')
def disconnect():
    print("Disconnected")
    
@sio.on('mouse')
def handle_mouse(message):
    capture.setMousePos(message["pos"]["x"], message["pos"]["y"])

@sio.on('mouseclick')
def handle_click():
    capture.click()

@sio.on('rightclick')
def handle_rightclick():
    capture.rightclick()

@sio.on('key')
def handle_mouse(message):
    capture.keypress(message['key'], message['alt'], message['ctrl'], message['shift'])

@sio.on('log')
def handle_log(message):
    print(message)
    
if __name__ == '__main__':
    sio.run(app, host="0.0.0.0", port=5000, debug=True)