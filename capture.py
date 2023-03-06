from win32 import win32api, win32gui
from ctypes import Structure, sizeof, create_string_buffer, windll
from ctypes.wintypes import (
    DWORD,
    LONG,
    WORD,
)

gdi32api = windll.gdi32

SRCCOPY = 0x00CC0020
CAPTUREBLT = 0x40000000
DIB_RGB_COLORS = 0
DI_NORMAL = 0x0003

class BITMAPINFOHEADER(Structure):
    """Information about the dimensions and color format of a DIB."""

    _fields_ = [
        ("biSize", DWORD),
        ("biWidth", LONG),
        ("biHeight", LONG),
        ("biPlanes", WORD),
        ("biBitCount", WORD),
        ("biCompression", DWORD),
        ("biSizeImage", DWORD),
        ("biXPelsPerMeter", LONG),
        ("biYPelsPerMeter", LONG),
        ("biClrUsed", DWORD),
        ("biClrImportant", DWORD),
    ]

class BITMAPINFO(Structure):
    """
    Structure that defines the dimensions and color information for a DIB.
    """

    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", DWORD * 3)]

def get_display_resolution():
    left = win32api.GetSystemMetrics(76)
    top = win32api.GetSystemMetrics(77)
    right = win32api.GetSystemMetrics(78)
    bottom = win32api.GetSystemMetrics(79)
    return {
        'left'  : int(left),
        'top'   : int(top),
        'width' : int(right - left),
        'height': int(bottom - top)
    }

def screenshot(left=0, top=0, width=100, height=100, cursor=True):
    source_dc = win32gui.GetWindowDC(0) # Source Device context

    # New BMP image, information filling
    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biPlanes = 1  # Always 1
    bmi.bmiHeader.biBitCount = 32  # RGBX
    bmi.bmiHeader.biCompression = 0  # no compression
    bmi.bmiHeader.biClrUsed = 0  # read as RGB Sequence
    bmi.bmiHeader.biClrImportant = 0  # read as RGB Sequence
    bmi.bmiHeader.biWidth = width
    bmi.bmiHeader.biHeight = -height

    mem_dc = gdi32api.CreateCompatibleDC(source_dc) # Target Device Context
    screen_bmp = gdi32api.CreateCompatibleBitmap(source_dc, width, height) # Bitmap Container
    gdi32api.SelectObject(mem_dc, screen_bmp) # Assign Bitmap to Target Device Context
    gdi32api.BitBlt(mem_dc, 0, 0, width, height, source_dc, left, top, SRCCOPY) # Copy Screen from SOurce

    if cursor:
        flags, hcursor, (cx,cy) = win32gui.GetCursorInfo()
        if flags != 0:
            # Cursor visible
            win32gui.DrawIcon(mem_dc, cx, cy, hcursor)

    data = create_string_buffer(width * height * 4) # Allocation of a buffer for data transfer
    bits = gdi32api.GetDIBits(mem_dc, screen_bmp, 0, height, data, bmi, DIB_RGB_COLORS) # Retrieve raw data
    
	# Cleanup
    gdi32api.DeleteObject(source_dc)
    gdi32api.DeleteObject(mem_dc)
    gdi32api.DeleteObject(screen_bmp)
    
    # Verify
    if bits != height:
        raise ValueError('Windows: GetDIBits() failed.')

    return data
