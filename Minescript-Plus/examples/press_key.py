"""
    @author RazrCraft
    @create date 2025-07-05 18:04:53
    @modify date 2025-07-13 13:12:02
    @desc Simple press key example
 """
from time import sleep
from minescript_plus import Key


# https://minecraft.wiki/w/Key_codes#Current
sleep(1)
Key.press_key("key.keyboard.e", True)
sleep(.1)
Key.press_key("key.keyboard.e", False)
