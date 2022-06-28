import ctypes
from typing import TypeAlias


# Native types
char: TypeAlias = ctypes.c_char
char_pointer: TypeAlias = ctypes.c_char_p
void_pointer: TypeAlias = ctypes.c_void_p
uint32: TypeAlias = ctypes.c_uint32

# Steamworks API types
AppId_t: TypeAlias = uint32
