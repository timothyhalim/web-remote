from win32 import win32api
import capture
import cv2
import base64
import numpy as np
import math

CURRENT_SCREEN = {}
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
SCREEN_COL = 0
SCREEN_ROW = 0
CHUNK_SIZE = 20

def grabScreen(new_session=False, split=False):
    global CURRENT_SCREEN
    global SCREEN_WIDTH
    global SCREEN_HEIGHT
    global SCREEN_COL
    global SCREEN_ROW

    if new_session:
        CURRENT_SCREEN = {}
    
    new_image = {}

    monitor = capture.get_display_resolution()
    SCREEN_WIDTH = monitor['width']
    SCREEN_HEIGHT = monitor['height']
    SCREEN_COL = math.ceil(SCREEN_WIDTH/CHUNK_SIZE)
    SCREEN_ROW = math.ceil(SCREEN_HEIGHT/CHUNK_SIZE)

    data = capture.screenshot(**monitor)
    image = np.frombuffer(bytearray(data), dtype=np.uint8)
    image = image.reshape((SCREEN_HEIGHT, SCREEN_WIDTH, 4))
    for x in range(SCREEN_COL):
        for y in range(SCREEN_ROW):
            # Slice the image to chunks
            chunk_array = image[
                    y*CHUNK_SIZE:min((y+1)*CHUNK_SIZE, SCREEN_HEIGHT),
                    x*CHUNK_SIZE:min((x+1)*CHUNK_SIZE, SCREEN_WIDTH)
                ]
                
            # Save to jpg
            _, frame_encoded = cv2.imencode('.jpg', 
                chunk_array, [int(cv2.IMWRITE_JPEG_QUALITY), 100]
            )

            # Convert to base64
            b64str =  "data:image/jpeg;base64,"+str(base64.b64encode(frame_encoded).decode('ascii'))

            # Compare and send only changed chunk
            current_chunk = CURRENT_SCREEN.get((x,y), None)
            if current_chunk != b64str:
                if not new_image.get(x):
                    new_image[x] = {}
                new_image[x][y] = b64str
                if not CURRENT_SCREEN.get(x):
                    CURRENT_SCREEN[x] = {}
                CURRENT_SCREEN[x][y] = b64str
 
    if new_session:
        return CURRENT_SCREEN
    else:
        return new_image

def grabScreen2():
    global SCREEN_WIDTH
    global SCREEN_HEIGHT

    monitor = capture.get_display_resolution()
    SCREEN_WIDTH = monitor['width']
    SCREEN_HEIGHT = monitor['height']

    while True:
        data = capture.screenshot(**monitor)
        image = np.frombuffer(bytearray(data), dtype=np.uint8)
        image = image.reshape((SCREEN_HEIGHT, SCREEN_WIDTH, 4))
        _, buffer = cv2.imencode('.jpg', 
            image, [int(cv2.IMWRITE_JPEG_QUALITY), 100]
        )
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                

def getMousePos():
    return win32api.GetCursorPos()

def setMousePos(x, y):
    win32api.SetCursorPos((int(x*SCREEN_WIDTH), int(y*SCREEN_HEIGHT)))

MOUSEACTION = {
    'left_down': 0x0002,
    'left_up': 0x0004,
    'right_down': 0x0008,
    'right_up': 0x0010,
}

def mouseEvent(key):
    action = MOUSEACTION.get(key)
    if action:
        win32api.mouse_event(action, 0, 0, 0, 0)

def click():
    win32api.mouse_event(
        MOUSEACTION.get('left_down') + 
        MOUSEACTION.get('left_up'), 
        0, 0, 0, 0)

def rightclick():
    win32api.mouse_event(
        MOUSEACTION.get('right_down') + 
        MOUSEACTION.get('right_up'), 
        0, 0, 0, 0)

def keypress(key, alt=False, ctrl=False, shift=False):
    key_map = {
        "KeyA": 0x41,
        "KeyB": 0x42,
        "KeyC": 0x43,
        "KeyD": 0x44,
        "KeyE": 0x45,
        "KeyF": 0x46,
        "KeyG": 0x47,
        "KeyH": 0x48,
        "KeyI": 0x49,
        "KeyJ": 0x4A,
        "KeyK": 0x4B,
        "KeyL": 0x4C,
        "KeyM": 0x4D,
        "KeyN": 0x4E,
        "KeyO": 0x4F,
        "KeyP": 0x50,
        "KeyQ": 0x51,
        "KeyR": 0x52,
        "KeyS": 0x53,
        "KeyT": 0x54,
        "KeyU": 0x55,
        "KeyV": 0x56,
        "KeyW": 0x57,
        "KeyX": 0x58,
        "KeyY": 0x59,
        "KeyZ": 0x5A,
        "Digit0": 0x30,
        "Digit1": 0x31,
        "Digit2": 0x32,
        "Digit3": 0x33,
        "Digit4": 0x34,
        "Digit5": 0x35,
        "Digit6": 0x36,
        "Digit7": 0x37,
        "Digit8": 0x38,
        "Digit9": 0x39,
        "Numpad0": 0x60,
        "Numpad1": 0x61,
        "Numpad2": 0x62,
        "Numpad3": 0x63,
        "Numpad4": 0x64,
        "Numpad5": 0x65,
        "Numpad6": 0x66,
        "Numpad8": 0x67,
        "Numpad7": 0x68,
        "Numpad9": 0x69,
        "NumpadMultiply": 0x6A,
        "NumpadAdd": 0x6B,
        "NumpadSeparator": 0x6C,
        "NumpadSubtract": 0x6D,
        "NumpadDecimal": 0x6E,
        "NumpadDivide": 0x6F,
        "NumpadEnter": 0x0D,
        "Minus": 0xBD,
        "Equal": 0xBB,
        "Backspace": 0x08,
        "Tab": 0x09,
        "Enter": 0x0D,
        "Backquote": 0xC0,
        "Comma": 0xBC,
        "Period": 0xBE,
        "Slash": 0xBF,
        "Semicolon": 0xBA,
        "Quote": 0xDE,
        "BracketLeft": 0xDB,
        "BracketRight": 0xDD,
        "Backslash": 0xDC,
        "ShiftLeft": 0xA0,
        "ShiftRight": 0xA1,
        "ControlLeft": 0xA2,
        "ControlRight": 0xA3,
        "AltLeft": 0xA4,
        "AltRight": 0xA5,
        "OSLeft": 0x5B,
        "OSRight": 0x5C,
        "Space": 0x20,
        "ArrowLeft": 0x25,
        "ArrowUp": 0x26,
        "ArrowRight": 0x27,
        "ArrowDown": 0x28,
        "Insert": 0x2D,
        "Delete": 0x2E,
        "PageUp": 0x21,
        "PageDown": 0x22,
        "End": 0x23,
        "Home": 0x24,
        "NumLock": 0x90,
        "ScrollLock": 0x91,
        "CapsLock": 0x14,
        "Pause": 0x13,
        "Escape": 0x1B,
        "Shift": 0x10,
        "Ctrl": 0x11,
        "Alt": 0x12,
        "Select": 0x29,
        "Print": 0x2A,
        "Execute": 0x2B,
        "PrintScreen": 0x2C,
        "Help": 0x2F,
        "F1": 0x70,
        "F2": 0x71,
        "F3": 0x72,
        "F4": 0x73,
        "F5": 0x74,
        "F6": 0x75,
        "F7": 0x76,
        "F8": 0x77,
        "F9": 0x78,
        "F10": 0x79,
        "F11": 0x7A,
        "F12": 0x7B,
        "F13": 0x7C,
        "F14": 0x7D,
        "F15": 0x7E,
        "F16": 0x7F,
        "F17": 0x80,
        "F18": 0x81,
        "F19": 0x82,
        "F20": 0x83,
        "F21": 0x84,
        "F22": 0x85,
        "F23": 0x86,
        "F24": 0x87,
        "BrowserHome": 0xAC,
        "BrowserSearch": 0xAA,
        "BrowserBack": 0xA6,
        "BrowserForward": 0xA7,
        "BrowserRefresh": 0xA8,
        "BrowserStop": 0xA9,
        "BrowserFavorites": 0xAB,
        "LaunchMail": 0xB4,
        "LaunchApp2": 0xB7,
        "MediaSelect": 0xB5,
        "MediaTrackPrevious": 0xB1,
        "MediaPlayPause": 0xB3,
        "MediaStop": 0xB2,
        "MediaTrackNext": 0xB0,
        "VolumeMute": 0xAD,
        "VolumeDown": 0xAE,
        "VolumeUp": 0xAF,
    }
    vk_key = key_map.get(key)
    if vk_key:
        shift_key = key_map.get("Shift")
        ctrl_key = key_map.get("Ctrl")
        alt_key = key_map.get("Alt")
        if shift: win32api.keybd_event(shift_key, 0, 0, 0)
        if ctrl: win32api.keybd_event(ctrl_key, 0, 0, 0)
        if alt: win32api.keybd_event(alt_key, 0, 0, 0)
        win32api.keybd_event(vk_key, 0, 0, 0) # Key Down
        win32api.keybd_event(vk_key, 0, 0x0002, 0) # Key Up
        if shift: win32api.keybd_event(shift_key, 0, 0x0002, 0)
        if ctrl: win32api.keybd_event(ctrl_key, 0, 0x0002, 0)
        if alt: win32api.keybd_event(alt_key, 0, 0x0002, 0)
    else:
        print("Unknown key: %s" %key)
    # print(code)12110645