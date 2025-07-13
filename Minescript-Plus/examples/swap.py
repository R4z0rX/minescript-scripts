"""
    @author RazrCraft
    @create date 2025-06-24 18:40:05
    @modify date 2025-07-13 13:05:30
    @desc Simple inventory-hotbar swap example
 """
from time import sleep
from minescript import press_key_bind
from minescript_plus import Inventory, Screen


press_key_bind("key.inventory", True)
r = Screen.wait_screen()
press_key_bind("key.inventory", False)
if not r:
    print("Can't find an inventory screen")
else:
    Inventory.inventory_hotbar_swap(22, 4)
    sleep(0.05)
    Screen.close_screen()
