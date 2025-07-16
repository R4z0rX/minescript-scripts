"""
    @author RazrCraft
    @create date 2025-07-08 12:59:08
    @modify date 2025-07-16 19:40:46
    @desc Simple actionbar event example using @Event.event decorator for registering the event
 """
import asyncio
from minescript import tick_loop
from minescript_plus import Event

loop: bool = True

@Event.event
def on_actionbar(text: str):
    global loop
    
    print(f"Actionbar changed! current value: {text}")
    loop = False

async def main():
    await Event.activate_all()
    print("Actionbar event test")
    print("You can use this command to testi it: /title @s actionbar \"Test!\"")
    print("Waiting for actionbar...")
    
    with tick_loop:
        while loop:
            await asyncio.sleep(0.05)


if __name__ == "__main__":
    asyncio.run(main())
