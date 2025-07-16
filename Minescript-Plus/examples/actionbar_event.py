"""
    @author RazrCraft
    @create date 2025-07-07 21:38:07
    @modify date 2025-07-16 19:40:13
    @desc Simple actionbar event example using Event.register method
 """
import asyncio
from minescript import tick_loop
from minescript_plus import Event

loop: bool = True

def on_actionbar(text: str):
    global loop
    
    print(f"Actionbar changed! current value: {text}")
    loop = False

async def main():
    listener = await Event.register("on_actionbar", on_actionbar)
    print("Actionbar event test")
    print("You can use this command to testi it: /title @s actionbar \"Test!\"")
    print("Waiting for actionbar...")

    with tick_loop:
        while loop:
            await asyncio.sleep(0.05)

    listener.unregister()


if __name__ == "__main__":
    asyncio.run(main())
