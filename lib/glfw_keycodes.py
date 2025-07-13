"""
    @author RazrCraft
    @create date 2025-07-08 13:26:41
    @modify date 2025-07-08 13:42:13
    @desc This enum provides all the standard GLFW key codes with their numeric values. You can use it in several ways:

          Direct enum access: GLFWKey.SPACE returns 32
          Function lookup: get_glfw_keycode('space') returns 32
          Iteration: You can iterate over all keys or check membership

          The enum inherits from IntEnum, so the values can be used directly as integers in comparisons and arithmetic operations. 
          The key codes match the official GLFW constants used in C/C++ GLFW applications.

          Example:
          from glfw_keycodes import GLFWKey, get_glfw_keycode

          print(GLFWKey.SPACE)
          print(get_glfw_keycode('space'))
"""
from enum import IntEnum

class GLFWKey(IntEnum):
    """GLFW Key codes enum with numeric values"""
    
    # Special keys
    UNKNOWN = -1
    
    # Printable keys
    SPACE = 32
    APOSTROPHE = 39  # '
    COMMA = 44       # ,
    MINUS = 45       # -
    PERIOD = 46      # .
    SLASH = 47       # /
    
    # Numbers
    KEY_0 = 48
    KEY_1 = 49
    KEY_2 = 50
    KEY_3 = 51
    KEY_4 = 52
    KEY_5 = 53
    KEY_6 = 54
    KEY_7 = 55
    KEY_8 = 56
    KEY_9 = 57
    
    # More printable keys
    SEMICOLON = 59   # ;
    EQUAL = 61       # =
    
    # Letters
    A = 65
    B = 66
    C = 67
    D = 68
    E = 69
    F = 70
    G = 71
    H = 72
    I = 73
    J = 74
    K = 75
    L = 76
    M = 77
    N = 78
    O = 79
    P = 80
    Q = 81
    R = 82
    S = 83
    T = 84
    U = 85
    V = 86
    W = 87
    X = 88
    Y = 89
    Z = 90
    
    # Brackets and backslash
    LEFT_BRACKET = 91   # [
    BACKSLASH = 92      # \
    RIGHT_BRACKET = 93  # ]
    GRAVE_ACCENT = 96   # `
    
    # World keys (non-US)
    WORLD_1 = 161
    WORLD_2 = 162
    
    # Function keys
    ESCAPE = 256
    ENTER = 257
    TAB = 258
    BACKSPACE = 259
    INSERT = 260
    DELETE = 261
    RIGHT = 262
    LEFT = 263
    DOWN = 264
    UP = 265
    PAGE_UP = 266
    PAGE_DOWN = 267
    HOME = 268
    END = 269
    CAPS_LOCK = 280
    SCROLL_LOCK = 281
    NUM_LOCK = 282
    PRINT_SCREEN = 283
    PAUSE = 284
    
    # Function keys F1-F25
    F1 = 290
    F2 = 291
    F3 = 292
    F4 = 293
    F5 = 294
    F6 = 295
    F7 = 296
    F8 = 297
    F9 = 298
    F10 = 299
    F11 = 300
    F12 = 301
    F13 = 302
    F14 = 303
    F15 = 304
    F16 = 305
    F17 = 306
    F18 = 307
    F19 = 308
    F20 = 309
    F21 = 310
    F22 = 311
    F23 = 312
    F24 = 313
    F25 = 314
    
    # Keypad
    KP_0 = 320
    KP_1 = 321
    KP_2 = 322
    KP_3 = 323
    KP_4 = 324
    KP_5 = 325
    KP_6 = 326
    KP_7 = 327
    KP_8 = 328
    KP_9 = 329
    KP_DECIMAL = 330
    KP_DIVIDE = 331
    KP_MULTIPLY = 332
    KP_SUBTRACT = 333
    KP_ADD = 334
    KP_ENTER = 335
    KP_EQUAL = 336
    
    # Modifier keys
    LEFT_SHIFT = 340
    LEFT_CONTROL = 341
    LEFT_ALT = 342
    LEFT_SUPER = 343
    RIGHT_SHIFT = 344
    RIGHT_CONTROL = 345
    RIGHT_ALT = 346
    RIGHT_SUPER = 347
    MENU = 348


# Alternative function-based approach
def get_glfw_keycode(key_name: str) -> int:
    """Get GLFW keycode by name (case-insensitive)"""
    try:
        return GLFWKey[key_name.upper()]
    except KeyError:
        return GLFWKey.UNKNOWN


# Usage examples
if __name__ == "__main__":
    # Using the enum
    print(f"SPACE key: {GLFWKey.SPACE}")           # 32
    print(f"ESC key: {GLFWKey.ESCAPE}")           # 256
    print(f"A key: {GLFWKey.A}")                  # 65
    print(f"F1 key: {GLFWKey.F1}")                # 290
    
    # Using the function
    print(f"W key: {get_glfw_keycode('W')}")      # 87
    print(f"Enter key: {get_glfw_keycode('enter')}")  # 257
    
    # Check if a key exists
    if GLFWKey.LEFT_SHIFT in GLFWKey:
        print(f"Left Shift: {GLFWKey.LEFT_SHIFT}")  # 340
