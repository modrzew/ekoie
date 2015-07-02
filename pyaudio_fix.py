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


def _py_error_handler(filename, line, function, err, fmt):
    pass


_ERROR_HANDLER_FUNC = CFUNCTYPE(
    None,
    c_char_p,
    c_int,
    c_char_p,
    c_int,
    c_char_p,
)
_c_error_handler = None


def fix_pyaudio():
    global _c_error_handler  # required to trick the garbage collector
    _c_error_handler = _ERROR_HANDLER_FUNC(_py_error_handler)
    _asound = cdll.LoadLibrary('libasound.so')
    _asound.snd_lib_error_set_handler(_c_error_handler)


__all__ = [
    'fix_pyaudio',
]
