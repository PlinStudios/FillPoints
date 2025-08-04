import ctypes
from PyQt5.QtCore import QByteArray
import struct

#load DLL
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
fill_lib = ctypes.CDLL(f"{dir_path}/fillcpp.dll")

fill_lib.expand_color_to_line.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte), #color data
    ctypes.POINTER(ctypes.c_ubyte), #line data
    ctypes.POINTER(ctypes.c_ubyte), #output buffer
    ctypes.c_int, #width
    ctypes.c_int, #height
    ctypes.c_ubyte #opacity threshold
]
fill_lib.expand_color_to_line.restype = None

fill_lib.expand_color_free.argtypes = [
    ctypes.POINTER(ctypes.c_ubyte), #color data
    ctypes.c_int, #width
    ctypes.c_int, #height
    ctypes.c_int #expansion
]
fill_lib.expand_color_free.restype = None

def fill(color_data, line_data, w, h, opacity_threshold):
    size = w * h * 4
    color_buf = (ctypes.c_ubyte * size).from_buffer_copy(color_data)
    line_buf = (ctypes.c_ubyte * size).from_buffer_copy(line_data)
    output_buf = (ctypes.c_ubyte * size)()

    fill_lib.expand_color_to_line(color_buf, line_buf, output_buf, w, h, opacity_threshold)

    return QByteArray(bytes(output_buf))

def extra_expand(color_data, w, h, expansion):
    size = w * h * 4
    color_buf = (ctypes.c_ubyte * size).from_buffer_copy(color_data)

    fill_lib.expand_color_free(color_buf, w, h, expansion)

    return QByteArray(bytes(color_buf))