# Minescript Plus

**Version:** 0.8-alpha  
**Author:** RazrCraft  
**Date:** 2025-07-16

User-friendly API for scripts that adds extra functionality to the Minescript mod, using [`lib_java`](https://minescript.net/sdm_downloads/lib_java-v2/) and other libraries.  
This module should be imported by other scripts and not run directly.

---

## Usage

First you need to download minescript_plus.py and place it in the /minescript folder (where config.txt is located, and probably your scripts too).

Import the module in your script:

```python
from minescript_plus import Inventory, Screen, Gui, Key, Client, Player, Server, World, Util
```

You don't need to import all the classes, just the ones you need. \
Use the classes and methods as shown in the examples below to interact with Minecraft via Minescript Plus.

---

## Classes & Methods

### [`Inventory`](Minescript-Plus/minescript_plus.py )
Provides methods for interacting with the player's inventory and other containers screens. \
<u>Slot IDs</u>: \
_Player inventory_: hotbar = 0-8, main = 9-35, offhand = 40, boots, leggins, chestplate, helmet = 36-39 \
_Single chest_ / _Trap chest_ / _Ender chest_ / _Shulker box_: 0-26 \
_Double chest_: 0-53 \
If you need to access the player's main inventory or hotbar with an open container, the slot IDs change. For example, if you have an open double chest (54 slots), then the main inventory will be from 54 to 80, and the hotbar slots IDs will be from 81 to 89. Refer to [this page](https://minecraft.wiki/w/Java_Edition_protocol/Inventory#Chest) for more information.

- **click_slot(slot: int) -> bool**  
  Simulates a left mouse click on a specified inventory slot.  
  *Returns:* `True` if successful, `False` if no screen is open.

- **shift_click_slot(slot: int) -> bool**  
  Simulates a shift-click action on a specified inventory slot.  
  *Returns:* `True` if successful, `False` if no screen is open.

- **inventory_hotbar_swap(inv_slot: int, hotbar_slot: int) -> bool**  
  Swaps an item between an inventory slot and a hotbar slot.  
  *Returns:* `True` if successful, `False` if no screen is open.

- **open_targeted_chest() -> bool**  
  Attempts to open the chest block currently targeted by the player.  
  *Returns:* `True` if a chest was opened, `False` otherwise.

- **take_items(slots: list[int]) -> bool**  
  Transfers items from specified slots to the player's inventory using quick move.  
  *Returns:* `True` if successful, `False` if no screen is open.

- **find_item(item_id: str, cust_name: str = "", container: bool=False, try_open: bool=False) -> int | None**  
  Finds the first inventory slot containing a specific item, optionally by matching a custom name, and optionally by searching an already opened container, or attempting to open a targeted one.  
  *Returns:* Slot ID or `None` if not found.

**Example:**
```python
from minescript_plus import Inventory
slot = Inventory.find_item("minecraft:diamond")
if slot is not None:
    Inventory.click_slot(slot)
```

---

### [`Screen`](Minescript-Plus/minescript_plus.py )
Methods for interacting with Minecraft GUI screens.

- **wait_screen(name: str = "", delay: int = 500) -> bool**  
  Waits for a screen with a specific name (or any screen) to become available.  
  *Returns:* `True` if detected, `False` otherwise.

- **close_screen() -> None**  
  Closes the currently open chest GUI by simulating an Escape key press.

---

### [`Gui`](Minescript-Plus/minescript_plus.py )
Methods for manipulating Minecraft's title, subtitle, and actionbar.

- **get_title() -> str | None**  
  Retrieves the current title.

- **get_subtitle() -> str | None**  
  Retrieves the current subtitle.

- **get_actionbar() -> str | None**  
  Retrieves and clears the current actionbar (overlay message).

- **set_title(text: str) -> None**  
  Sets the title to the specified text.

- **set_subtitle(text: str) -> None**  
  Sets the subtitle to the specified text.

- **set_actionbar(text: str, tinted: bool = False) -> None**  
  Sets the actionbar to the specified text.

- **set_title_times(fadeInTicks: int, stayTicks: int, fadeOutTicks: int) -> None**  
  Sets the timing for the title and subtitle display.

- **reset_title_times() -> None**  
  Resets the title and subtitle display times to default.

- **clear_titles() -> None**  
  Clears the title and subtitle.

**Example:**
```python
from minescript_plus import Gui
Gui.set_title("Welcome!")
Gui.set_subtitle("Enjoy your game")
Gui.set_actionbar("Actionbar message", tinted=True)
```

---

### [`Key`](Minescript-Plus/minescript_plus.py )
Methods for simulating key presses.

- **press_key(key_name: str, state: bool) -> None**  
  Simulates pressing or releasing a key by name.

---

### [`Client`](Minescript-Plus/minescript_plus.py )
Methods for client-level actions.

- **pause_game() -> bool**  
  Open game menu.

- **is_local_server() -> bool**  
  Determines if the server is running locally (is single player).

- **disconnect() -> None**  
  Disconnects the current Minecraft network connection with a custom message.

---

### [`Player`](Minescript-Plus/minescript_plus.py )
Methods for retrieving player information.

- **get_latency() -> int**  
  Gets the player's network latency.

- **get_game_mode() -> str**  
  Retrieves the player's current game mode.

- **is_creative() -> bool**  
  Checks if the player is in creative mode.

- **is_survival() -> bool**  
  Checks if the player is in survival mode.

- **get_skin_url() -> str**  
  Retrieves the URL of the player's skin texture.

- **get_food_level() -> float**  
  Retrieves the player's food level.

- **get_saturation_level() -> float**  
  Retrieves the player's saturation level.

---

### [`Server`](Minescript-Plus/minescript_plus.py )
Methods for retrieving server information.

- **is_local() -> bool**  
  Determines if the server is running locally.

- **get_ping() -> int | None**  
  Retrieves the ping value from the current server.

- **is_lan() -> bool | None**  
  Determines if the server is running in LAN mode.

- **is_realm() -> bool | None**  
  Determines if the current server is a Realm.

---

### [`World`](Minescript-Plus/minescript_plus.py )
Methods for retrieving world information.

- **is_raining() -> bool**  
  Checks if it is currently raining.

- **is_thundering() -> bool**  
  Checks if it is currently thundering.

- **is_hardcore() -> bool**  
  Checks if the world is in hardcore mode.

- **get_difficulty() -> Difficulty**  
  Retrieves the current difficulty setting.

- **get_spawn_pos()**  
  Retrieves the spawn position.

- **get_game_time() -> int**  
  Returns the current game time in ticks.

- **get_day_time() -> int**  
  Returns the current day time in ticks.

---

### [`Util`](Minescript-Plus/minescript_plus.py )
Utility methods.

- **get_job_id(cmd: str) -> int | None**  
  Returns the job ID of a job matching the given command string, or `None` if not found.

---

## Events

There are a few events for now:
| Event Name  | Fires when  | Returns |
|:----------- |:----------- |:------- |
| on_title        | Title text change | New title text
| on_subtitle     | Subtitle text change | New subtitle text
| on_actionbar    | Actionbar text change | New actionbar text
| on_open_screen  | Any screen is opened  | The name of the screen  |

### [`Event`](Minescript-Plus/minescript_plus.py)
Provides an event system for registering and handling custom or built-in Minescript Plus events.

- **register(event_name: str, callback: Callable, once: bool = False) -> Listener**  
  Registers a callback for the specified event name.  
  If `once` is `True`, the listener will automatically unregister after the first trigger.  
  *Returns:* A `Listener` instance, which can be manually unregistered.

- **event(func: Callable) -> Callable**  
  Decorator that marks a function as an event listener.  
  The function name must match the event name.  
  All decorated functions must be activated later using `Event.activate_all()`.

- **activate_all() -> None**  
  Starts all listeners that were registered using the `@Event.event` decorator.

**Examples:**

Registering an existing event manually:
```python
from minescript_plus import Event

def on_actionbar(text: str):
    print(f"Actionbar updated: {text}")

# In your main asyncio function:
listener = await Event.register("on_actionbar", on_actionbar)
```

Registering an event using the decorator:
```python
from minescript_plus import Event

@Event.event
def on_actionbar(text: str):
    print(f"Actionbar updated: {text}")

# Later, in your main asyncio function:
await Event.activate_all()
```

---

## Notes

As this is an alpha version, expect possible breaking changes in the future.

---

## License

MIT © 2025 RazrCraft
