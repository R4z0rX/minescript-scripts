"""
    @author RazrCraft
    @create date 2025-06-13 18:19:36
    @modify date 2025-06-14 01:02:26
    @desc A really simple script that emulates the behavior of the MC key.command which opens the chat with the "/" ready 
          to enter a command.
          In this case, pressing "\" in my keyboard, opens the chat with the "\" ready to enter a Minescript command.
          To change the key bind, just change the value of the key_code variable.
          Additionally, to always have this functionality available, I added the following line to the config.txt file:
          autorun[*]=ms_key_command 

 """
from minescript import EventQueue, EventType, show_chat_screen

# Key bind (For other values, look here: https://www.glfw.org/docs/3.4/group__keys.html)
key_code = 96

with EventQueue() as event_queue:
    event_queue.register_key_listener()
    while True:
        event = event_queue.get()
        if event.type == EventType.KEY:
            if event.action == 0 and event.key == key_code:
                show_chat_screen(True, "\\")
