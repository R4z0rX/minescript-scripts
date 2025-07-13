"""
    @author RazrCraft
    @create date 2025-07-08 13:20:10
    @modify date 2025-07-08 14:09:13
    @desc Example of a key listener service to associate macros with keybinds
 """
from minescript import EventQueue, EventType, show_chat_screen, execute
from glfw_keycodes import GLFWKey, get_glfw_keycode # pylint: disable=W0611 # type: ignore


with EventQueue() as event_queue:
    event_queue.register_key_listener()
    while True:
        event = event_queue.get()
        if event.type == EventType.KEY and event.action == 0:
            match (event.key):
                case GLFWKey.GRAVE_ACCENT:
                    show_chat_screen(True, "\\")
                case GLFWKey.F6:
                    execute("\\jobs")
                case GLFWKey.F7:
                    show_chat_screen(True, "\\killjob ")
                case GLFWKey.F8:
                    show_chat_screen(True, "\\z ")
                case GLFWKey.F10:
                    execute("\\gui")
                case _:
                    pass
