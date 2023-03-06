from flask import Flask, render_template_string, Response
from flask_socketio import SocketIO
import emulate

app = Flask(__name__)
app.secret_key = 'your secret here'
sio = SocketIO(app)

@app.route("/")
def hello_world():
    screen = emulate.grabScreen(new_session=True)
    hstr = ""
    with open("home.html", "r") as html:
        hstr = html.read()

    return render_template_string(
        hstr, 
        width=emulate.SCREEN_ROW, 
        height=emulate.SCREEN_COL,
        data=screen,
        split=False
    )

from threading import Lock
thread = None
thread_lock = Lock()

def background_task():
    while True:
        sio.sleep(0.1)
        screen_data = emulate.grabScreen()
        if screen_data:
            sio.emit('image_change', {'data': screen_data })

@sio.on('connect')
def connect():
    print("Connected")
    if emulate.CURRENT_SCREEN:
        sio.emit('image_change', {'data': emulate.CURRENT_SCREEN })
    global thread
    with thread_lock:
        if thread is None:
            thread = sio.start_background_task(background_task)


@sio.on('disconnect')
def disconnect():
    print("Disconnected")

# Screen Share

@app.route('/video_feed')
def video_feed():
    return Response(emulate.grabScreen2(), mimetype='multipart/x-mixed-replace; boundary=frame')

# MOUSE EVENT

@sio.on('mousemove')
def handle_mouse(message):
    emulate.setMousePos(message["pos"]["x"], message["pos"]["y"])

@sio.on('mouseevent')
def handle_mouse(event):
    emulate.mouseEvent(event["key"])

@sio.on('mouseclick')
def handle_click():
    emulate.click()

@sio.on('rightclick')
def handle_rightclick():
    emulate.rightclick()

# KEYBOARD EVENT

@sio.on('key')
def handle_mouse(message):
    emulate.keypress(message['key'], message['alt'], message['ctrl'], message['shift'])

@sio.on('log')
def handle_log(message):
    print(message)
    
if __name__ == '__main__':
    sio.run(app, host="0.0.0.0", port=5000, debug=True)