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

        # # Get frame generator
        # gen = capture.ffmpegGrab()

        # new_image = {}
        # while True:
        #     # Read next frame from ffmpeg
        #     frame_array = next(gen)
        #     for x in range(capture.SCREEN_COL):
        #         for y in range(capture.SCREEN_ROW):
        #             # Slice the image to chunks
        #             chunk_array = frame_array[
        #                     y*capture.CHUNK_SIZE:min((y+1)*capture.CHUNK_SIZE, capture.SCREEN_HEIGHT),
        #                     x*capture.CHUNK_SIZE:min((x+1)*capture.CHUNK_SIZE, capture.SCREEN_WIDTH)
        #                 ]
                        
        #             # Save to jpg
        #             _, frame_encoded = capture.cv2.imencode('.jpg', 
        #                 chunk_array, [int(capture.cv2.IMWRITE_JPEG_QUALITY), 100]
        #             )

        #             # Convert to base64
        #             b64str =  "data:image/jpeg;base64,"+str(capture.base64.b64encode(frame_encoded).decode('ascii'))

        #             # Compare and send only changed chunk
        #             current_chunk = capture.CURRENT_SCREEN.get((x,y), None)
        #             if current_chunk != b64str:
        #                 if not new_image.get(x):
        #                     new_image[x] = {}
        #                 new_image[x][y] = b64str
        #                 if not capture.CURRENT_SCREEN.get(x):
        #                     capture.CURRENT_SCREEN[x] = {}
        #                 capture.CURRENT_SCREEN[x][y] = b64str

@sio.on('connect')
def connect():
    print("Connected")
    if capture.CURRENT_SCREEN:
        sio.emit('image_change', {'data': capture.CURRENT_SCREEN })
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