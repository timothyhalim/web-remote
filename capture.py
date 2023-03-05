from mss import mss
import cv2
import base64
import numpy as np
import math
from ctypes import windll, Structure, byref, c_long

CURRENT_SCREEN = {}
SCREEN_WIDTH = 0
SCREEN_HEIGHT = 0
SCREEN_COL = 0
SCREEN_ROW = 0
CHUNK_SIZE = 20

def grabScreen(new_session=False):
    global CURRENT_SCREEN
    global SCREEN_WIDTH
    global SCREEN_HEIGHT
    global SCREEN_COL
    global SCREEN_ROW

    if new_session:
        CURRENT_SCREEN = {}
    
    new_image = {}
    with mss() as sct:
        monitor = sct.monitors[0]
        SCREEN_WIDTH = monitor['width']
        SCREEN_HEIGHT = monitor['height']
        SCREEN_COL = math.ceil(SCREEN_WIDTH/CHUNK_SIZE)
        SCREEN_ROW = math.ceil(SCREEN_HEIGHT/CHUNK_SIZE)

        image = sct.grab(sct.monitors[0])
        frame_array = np.array(image)
        for x in range(SCREEN_COL):
            for y in range(SCREEN_ROW):
                # Slice the image to chunks
                chunk_array = frame_array[
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

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

def getMousePos():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return { "x": pt.x, "y": pt.y}

def setMousePos(x, y):
    windll.user32.SetCursorPos(int(x*SCREEN_WIDTH), int(y*SCREEN_HEIGHT))

def click():
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_CLICK = MOUSEEVENTF_LEFTDOWN + MOUSEEVENTF_LEFTUP

    windll.user32.mouse_event(MOUSEEVENTF_CLICK, 0, 0, 0, 0)

def rightclick():
    MOUSEEVENTF_RIGHTDOWN = 0x0008 
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_RIGHTCLICK = MOUSEEVENTF_RIGHTDOWN + MOUSEEVENTF_RIGHTUP

    windll.user32.mouse_event(MOUSEEVENTF_RIGHTCLICK, 0, 0, 0, 0)

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
        if shift: windll.user32.keybd_event(shift_key, 0, 0, 0)
        if ctrl: windll.user32.keybd_event(ctrl_key, 0, 0, 0)
        if alt: windll.user32.keybd_event(alt_key, 0, 0, 0)
        windll.user32.keybd_event(vk_key, 0, 0, 0) # Key Down
        windll.user32.keybd_event(vk_key, 0, 0x0002, 0) # Key Up
        if shift: windll.user32.keybd_event(shift_key, 0, 0x0002, 0)
        if ctrl: windll.user32.keybd_event(ctrl_key, 0, 0x0002, 0)
        if alt: windll.user32.keybd_event(alt_key, 0, 0x0002, 0)
    else:
        print("Unknown key: %s" %key)
    # print(code)12110645