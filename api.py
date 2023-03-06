from flask import Flask, render_template_string, Response
from flask_socketio import SocketIO
import capture

app = Flask(__name__)
app.secret_key = 'your secret here'
sio = SocketIO(app)

@app.route("/")
def hello_world():
    hstr = ""
    with open("home.html", "r") as html:
        hstr = html.read()

    return render_template_string(hstr)

@sio.on('connect')
def connect():
    print("Connected")

@sio.on('disconnect')
def disconnect():
    print("Disconnected")

# Screen Share

@app.route('/video_feed')
def video_feed():
    return Response(capture.grabScreen2(), mimetype='multipart/x-mixed-replace; boundary=frame')

# MOUSE EVENT

@sio.on('mousemove')
def handle_mouse(message):
    capture.setMousePos(message["pos"]["x"], message["pos"]["y"])

@sio.on('mouseevent')
def handle_mouse(event):
    capture.mouseEvent(event["key"])

@sio.on('mouseclick')
def handle_click():
    capture.click()

@sio.on('rightclick')
def handle_rightclick():
    capture.rightclick()

# KEYBOARD EVENT

@sio.on('key')
def handle_mouse(message):
    capture.keypress(message['key'], message['alt'], message['ctrl'], message['shift'])

@sio.on('log')
def handle_log(message):
    print(message)
    
if __name__ == '__main__':
    sio.run(app, host="0.0.0.0", port=5000, debug=True)