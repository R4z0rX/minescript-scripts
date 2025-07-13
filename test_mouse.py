"""
    @author RazrCraft
    @create date 2025-06-25 15:10:35
    @modify date 2025-06-25 15:34:46
    @desc Simple external mouse library test
 """
from time import sleep
import mouse
from minescript import press_key_bind

sleep(1)
press_key_bind("key.inventory", True)
sleep(.1)
press_key_bind("key.inventory", False)
sleep(1)
mouse.move(851, 541)
sleep(1)
mouse.click()
sleep(1)
last_position = (0, 0)
loop = True
while loop:
    position = mouse.get_position()
    if last_position != position:
        print(position)
        last_position = position
    if position == (0, 0):
        loop = False
