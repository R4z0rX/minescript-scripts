"""
    @author RazrCraft
    @create date 2025-08-18 04:41:54
    @modify date 2025-08-23 10:32:32
    @desc Very basic example of trading
 """
from time import sleep
from minescript import press_key_bind, player_look_at, screen_name
from minescript_plus import Trading, World, Screen

def get_trade_offers():
    current_screen = screen_name()
    #print(f"{current_screen}")
    if current_screen is not None and (current_screen == "Wandering Trader" or current_screen == "Librarian"):        
        offer = 0
        # Print some info (not necessary to make the trade later)
        cost_a = Trading.get_costA(offer, True)
        print(f"Cost A: {cost_a}")
        cost_b = Trading.get_costB(offer, True)
        print(f"Cost B: {cost_b}")
        result = Trading.get_result(offer, True)
        print(f"Result: {result}")
        
        # Made the trade (you only need the offer index, 0 is the first)
        Trading.trade_offer(offer)

        Screen.close_screen()

#sleep(1)
e = World.find_nearest_entity(type_str="villager")
if e:
    #player_look_at(*e.position)
    x, y, z = e.position
    player_look_at(x, y+1, z)
    press_key_bind("key.use", True)
    sleep(.1)
    press_key_bind("key.use", False)
    sleep(.5)
    get_trade_offers()
