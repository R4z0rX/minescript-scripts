# Minescript Plus

**Version:** 0.14.1-alpha  
**Author:** RazrCraft  
**Date:** 2025-09-25

User-friendly API for scripts that adds extra functionality to the Minescript mod.  
This module should be imported by other scripts and not run directly.

---

## Requirements

**For Minescript Plus v0.13-alpha or newer:**
* Minecraft (any version supported by Minescript)
* Minescript 5.0b6 or newer
* Python 3.10 or higher
* java module (already included with Minescript)
* Mappings (if you use Fabric, in chat: `\install_mappings` - More info [`here`](https://minescript.net/mappings))
* Fabric API mod (optional, for `Hud` class only) 
* [`lib_nbt v1`](https://minescript.net/sdm_downloads/lib_nbt-v1/) (optional, for `Inventory.find_item()` only)

\
For Minescript Plus v0.12-alpha or earlier:
(Although I never tried it on versions before 1.21.4)

* Minecraft (any version supported by Minescript)
* Minescript 5.0b3 or earlier
* Python 3.10 or higher
* [`lib_java v2`](https://minescript.net/sdm_downloads/lib_java-v2/)
* [`lib_nbt v1`](https://minescript.net/sdm_downloads/lib_nbt-v1/) (optional, for `Inventory.find_item()` only)

## Usage

First you need to download minescript_plus.py and place it in the /minescript folder (where config.txt is located, and probably your scripts too).

Import the module in your script:

```python
from minescript_plus import Inventory, Screen, Gui, Key, Client, Player, Server, World, Trading, Hud, Util, Keybind, Event
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

- **click_slot(slot: int, right_button: bool=False) -> bool**  
  Simulates a left (or right) mouse click on a specified inventory slot.  
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
  *Returns:* Slot ID or `None` if not found. \
  <u>Note</u>: This feature use [**lib_nbt**](https://minescript.net/sdm_downloads/lib_nbt-v1/).

**Example:**
```python
from minescript_plus import Inventory
slot = Inventory.find_item("minecraft:diamond")
if slot is not None:
    Inventory.click_slot(slot)
```

- **count_total(inventory: list[ItemStack], item_id: int) -> int**  
  Counts the total number of items with a specific item ID in the given inventory.  
  *Returns:* The total count of items with the specified item ID.

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
  Simulates pressing or releasing a key by name. (List of key codes used by Minecraft: https://minecraft.wiki/w/Key_codes#Current)

---

### [`Client`](Minescript-Plus/minescript_plus.py )
Methods for client-level actions.

- **pause_game() -> bool**  
  Open game menu.

- **is_local_server() -> bool**  
  Determines if the server is running locally (is single player).

- **is_multiplayer_server() -> bool**
  Determines whether the current Minecraft instance is connected to a multiplayer server.

- **disconnect() -> None**  
  Disconnects the current Minecraft network connection with a custom message.

- **get_options()**  
  Returns an instance of the game options.  
  Use `Client.get_options().<option_name>().value` to get an option value.
  Use `Client.get_options().<option_name>().set(<value>)` to set an option value. 

**Example:**
```python
from minescript_plus import Client
options = Client.get_options()
print("FOV:", options.fov().value)
print("Gamma:", .options.gamma().get())
options.fov().set(90)
```

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

- **get_tablist() -> list[dict[str,Any]]**  
  Retrieves a list of dictionaries containing information about all online players in the tab list.  
  Each dictionary contains keys: "Name", "UUID", "Latency", "GameMode", "SkinURL", "TablistOrder", and optionally "Team".

**Example:**
```python
from minescript_plus import Server
tablist = Server.get_tablist()
for player in tablist:
    print(player["Name"], player["Latency"])
```

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

- **get_targeted_sign_text() -> list[str]**  
  Retrieves the text from both the front and back sides of the sign block currently targeted by the player.  
  *Returns:* A list containing the text lines from the targeted sign (first four elements are the front, next four are the back).
---

### [`Trading`](Minescript-Plus/minescript_plus.py)

Methods for interacting with Minecraft villager trading screens and offers.

- **get_offers() -> MerchantOffers**  
  Retrieves all merchant offers available in the current trading screen.  
  *Returns:* The offers object, or `None` if no trading screen is open.

- **get_offer(offer_index: int) -> MerchantOffer**  
  Retrieves a specific merchant offer by index.  
  *Returns:* The offer object, or `None` if not available.

- **get_costA(offer_index: int, name_and_count: bool=False) -> tuple[str, int] | ItemStack | None**  
  Gets the first cost item (costA) for a merchant offer. If `name_and_count` is `True`, returns a tuple `(name, count)`; otherwise returns the `ItemStack`.  
  *Returns:* ItemStack or (name, count) tuple, or `None` if not available.

- **get_costB(offer_index: int, name_and_count: bool=False) -> tuple[str, int] | ItemStack | None**  
  Gets the second cost item (costB) for a merchant offer. If `name_and_count` is `True`, returns a tuple `(name, count)`; otherwise returns the `ItemStack`.  
  *Returns:* ItemStack or (name, count) tuple, or `None` if not available.

- **get_result(offer_index: int, name_and_count: bool=False) -> tuple[str, int] | ItemStack | None**  
  Gets the result item for a merchant offer. If `name_and_count` is `True`, returns a tuple `(name, count)`; otherwise returns the `ItemStack`.  
  *Returns:* ItemStack or (name, count) tuple, or `None` if not available.

- **trade_offer(offer_index: int) -> bool**  
  Executes a trade for the specified merchant offer index.  
  *Returns:* `True` if trade was attempted, `False` if no trading screen is open.

**Example:**
```python
from minescript_plus import Trading

# Get all offers
offers = Trading.get_offers()

# Get the cost and result of the first offer
costA = Trading.get_costA(0, name_and_count=True)
costB = Trading.get_costB(0, name_and_count=True)
result = Trading.get_result(0, name_and_count=True)
print("CostA:", costA)
print("CostB:", costB)
print("Result:", result)

# Trade the first offer
if offers:
    Trading.trade_offer(0)
```

---

### [`Hud`](Minescript-Plus/minescript_plus.py)

Methods for rendering custom text and items on the Minecraft HUD (Heads-Up Display). Requires **Fabric API** mod.

- **add_text(text: str, x: int, y: int, color: tuple=(255,255,255), alpha: int=255, scale: float=1.0, shadow: bool=False, italic: bool=False, underline: bool=False, strikethrough: bool=False, obfsucated: bool=False) -> int**  
  Adds a styled text string to the HUD at the specified position.  
  *Returns:* The index of the added text.

- **set_text(index: int, text: str) -> None**  
  Change the text of an existing entry with the given index.

- **remove_text(index: int) -> None**  
  Removes the text with the given index.

- **clear_texts() -> None**  
  Removes all custom HUD texts.

- **get_texts() -> dict[int, tuple]**  
  Returns a dictionary of all HUD texts and their properties.

- **show_hud(enable: bool) -> None**  
  Shows or hides all custom HUD elements.

- **show_text(index: int, enable: bool) -> None**  
  Shows or hides a specific HUD text by index.

- **use_toggle_key(enable: bool) -> None**  
  Enables or disables the toggle key for showing/hiding the HUD.

- **set_toggle_key(toggle_key: int) -> None**  
  Sets the key code used to toggle the HUD display.

- **get_item_from_itemid(item_id: str)**  
  Returns the item object for a given item ID.

- **get_itemid_from_block_type(block_type: str) -> str**  
  Gets the item ID corresponding to a block type.

- **get_item_name(item) -> str**  
  Returns the display name of an item.

- **add_item(item_id: str, x: int, y: int, count: str="", scale: float=1.0) -> int**  
  Adds an item icon to the HUD at the specified position.  
  *Returns:* The index of the added item.

- **remove_item(index: int) -> None**  
  Removes the item with the given index.

- **clear_items() -> None**  
  Removes all custom HUD items.

- **get_items() -> dict[int, tuple]**  
  Returns a dictionary of all HUD items and their properties.

- **show_item(index: int, enable: bool) -> None**  
  Shows or hides a specific HUD item by index.

**Example:**
```python
from minescript_plus import Hud

# Add custom text to the HUD
text_id = Hud.add_text("Hello World!", x=10, y=10, color=(0,255,0), scale=1.5, shadow=True)

# Add an item icon to the HUD
item_id = Hud.add_item("minecraft:diamond", x=50, y=10, count="5", scale=1.2)

# Hide/show HUD elements
Hud.show_hud(True)
Hud.show_text(text_id, False)
Hud.show_item(item_id, True)
```

---

### [`Util`](Minescript-Plus/minescript_plus.py )
Utility methods.

- **get_job_id(cmd: str) -> int | None**  
  Returns the job ID of a job matching the given command string, or `None` if not found.

- **get_clipboard() -> str**  
  Retrieves the current contents of the system clipboard.

- **set_clipboard(string: str) -> int | None**  
  Sets the system clipboard to the specified string.

- **get_distance(pos1: list, pos2: list | None=None) -> float**  
  Calculates the Euclidean distance between two 3D positions.
  If pos2 isn't defined, defaults to the current player position.
  
- **get_nbt(obj: dict, path: str, default=None) -> Any**  
  Get a value from nested SNBT data using dot notation.

**Example:**
```python
import lib_nbt
from minescript_plus import Util

snbt: str = '{Brain: {memories: {"minecraft:job_site": {value: {pos: [I; 9, -60, 17],dimension: "minecraft:overworld"}}}}'
nbt: dict = lib_nbt.parse_snbt(snbt.replace("I;", ""))
value = Util.get_nbt(nbt, "Brain.memories.minecraft:job_site.value")
print(value) # Prints: {'pos': [9, -60, 17], 'dimension': 'minecraft:overworld'}
print(value.get("pos")) # Prints: [9, -60, 17]
print(Util.get_nbt(value, "dimension", "default value")) # Prints: minecraft:overworld
print(Util.get_nbt(value, "non_existant_key", "default value")) # Prints: default value
```

- **get_light_level(block_pos=None, source: str="RAW") -> int**  
  Returns the light level at a specified block position in the Minecraft world.  
  - `block_pos`: The position to check (defaults to the player's current block position).  
  - `source`: `"RAW"` for raw brightness, `"SKY"` for sky light, or `"BLOCK"` for block light.  
  *Returns:* The light level as an integer.

**Example:**
```python
from minescript_plus import Util

raw = Util.get_light_level(source="RAW")
sky = Util.get_light_level(source="SKY")
block = Util.get_light_level(source="BLOCK")
print(f"Client Light: {raw} ({sky} sky, {block} block)")
```

- **play_sound(sound=None) -> None**  
  Plays a sound on the client side.  
  - `sound` (optional): The sound event to play. Should be an instance from the `SoundEvents` class.
                Defaults to `EXPERIENCE_ORB_PICKUP` if None is provided.
  - `sound_source` (optional): The source of the sound. Should be an instance from the `SoundSource` class.
                Defaults to `PLAYERS` if None is provided.
  - `volume` (float, optional): The volume of the sound, clamped between `0.0` and `1.0`. Defaults to `1.0`.
  - `pitch` (float, optional): The pitch of the sound, clamped between `0.0` and `2.0`. Defaults to `1.0`.

**Example:**
```python
from minescript_plus import Util

Util.play_sound() # Experience orb pickup "ding" sound
Util.play_sound(Util.get_soundevents().PLAYER_LEVELUP)
```

- **get_soundevents()**  
  Returns the `SoundEvents` class from Minecraft, which can be used to get a sound for the `play_sound()` method.  
  See all available sounds [here](https://mappings.dev/1.21.8/net/minecraft/sounds/SoundEvents.html).

- **get_soundsource()**  
  Returns the `SoundSource` class from Minecraft, which can be used to get a sound_source for the `play_sound()` method.  
  See all available sound_sources [here](https://mappings.dev/1.21.8/net/minecraft/sounds/SoundSource.html).

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

## Keybind

The `Keybind` class allows you to register, modify, and remove custom keybinds that trigger Python callbacks when specific keys are pressed in Minecraft. Key codes use [GLFW Keyboard key tokens](https://www.glfw.org/docs/3.4/group__keys.html).
For simplicity, you can use [glfw_key_codes.py](https://github.com/R4z0rX/minescript-scripts/blob/main/lib/glfw_keycodes.py).
 
### [`Keybind`](Minescript-Plus/minescript_plus.py)

- **set_keybind(key: int, callback: Callable[[], None], name: str = "", category: str = "", description: str = "") -> None**  
  Registers a new keybind for the given key code. The callback will be called when the key is pressed. Optional metadata (name, category, description) is for display/documentation purposes.

- **modify_keybind(key: int, callback: Callable[[], None], name: str = "", category: str = "", description: str = "") -> None**  
  Modifies an existing keybind for the given key code. Raises an error if the keybind does not exist.

- **remove_keybind(key: int) -> None**  
  Removes the keybind for the given key code. Raises an error if the keybind does not exist.

**Example:**
```python
from minescript_plus import Keybind

def on_f5():
    print("F5 was pressed!")

kb = Keybind()

kb.set_keybind(294, on_f5)
# or with glfw_key_codes.py (remember to import it)
kb.set_keybind(GLFWKey.F5, on_f5)
```

---

## Notes

As this is an alpha version, expect possible breaking changes in the future.

---

## License

MIT © 2025 RazrCraft
