# Minescript Plus

**Version:** 0.6-alpha  
**Author:** RazrCraft  
**Date:** 2025-07-12

User-friendly API for scripts that adds extra functionality to the Minescript mod, using [`lib_java`](src/lib/lib_java.py ) and other libraries.  
This module should be imported by other scripts and not run directly.

---

## Classes & Methods

### [`Inventory`](Minescript-Plus/minescript_plus.py )
Provides methods for interacting with the player's inventory and screens.

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

- **find_item(item_id: str, cust_name: str = "") -> int | None**  
  Finds the first inventory slot containing a specified item, optionally matching a custom name.  
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

## Usage

Import the module in your script:

```python
from minescript_plus import Inventory, Screen, Gui, Key, Client, Player, Server, World, Util
```

Use the classes and methods as shown in the examples above to interact with Minecraft via Minescript Plus.

---

## License

MIT © 2025 RazrCraft
