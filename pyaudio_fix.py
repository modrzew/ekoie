"""Fix for pyaudio (or rather portaudio) debug messages

These get very annoying and break npyscreen interface, even though everything
works properly.

Stolen from http://stackoverflow.com/q/7088672
"""
from ctypes import (
    CFUNCTYPE,
    c_char_p,
    c_int,
    cdll
)


def py_error_handler(filename, line, function, err, fmt):
    pass


ERROR_HANDLER_FUNC = CFUNCTYPE(
    None,
    c_char_p,
    c_int,
    c_char_p,
    c_int,
    c_char_p,
)


def fix_pyaudio():
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
