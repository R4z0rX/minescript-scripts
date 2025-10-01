"""
    Minescript Plus
    Version: 0.15.0-alpha
    Author: RazrCraft
    Date: 2025-09-30

    User-friendly API for scripts that adds extra functionality to the
    Minescript mod, using lib_java and other libraries.
    This module should be imported by other scripts and not run directly.

    Usage: Similar to Minescript, import minescript_plus  # from Python script

    Minimum requirements: Minecaft 1.21.8, Minescript 5.0b6, Python 3.10
    
    Note: Some code shared by @maxuser (Minescript's creator) on the 
    official discord was used in this API, mostly in the Inventory class.
"""
import asyncio
import threading
from os import path
from sys import exit, stderr, version # pylint: disable=W0622
from time import sleep
from math import floor
from typing import Callable, Literal, Any
from dataclasses import dataclass, asdict
from minescript import (set_default_executor, EventQueue, EventType, EntityData, script_loop, render_loop, ItemStack, TargetedBlock,
                        player_inventory, player_get_targeted_block, press_key_bind, screen_name, player_name,
                        job_info, container_get_items, player_position, entities, echo_json)
from minescript import VersionInfo as VF
from minescript import version_info as ver_info
from java import JavaClass, eval_pyjinn_script

lib_nbt_module: bool = True
try:
    import lib_nbt
except ModuleNotFoundError:
    lib_nbt_module = False

set_default_executor(script_loop)

_ver: str = "0.15.0-alpha"

if __name__ == "__main__":
    print(f"Minescript Plus v{_ver}\n\nDon't run it, it's a module, you should import it in your scripts.")
    exit(1)

_mc_ver = ver_info().minecraft
_map_path1 = f"minescript/system/mappings/{_mc_ver}/{_mc_ver}.tiny"
_map_path2 = f"minescript/system/mappings/{_mc_ver}/client.txt"

if not path.exists(_map_path1) or not path.exists(_map_path2):
    print("Error: No mappings found. Use this in chat first: \\install_mappings")
    exit(1)

fabric = ver_info().minecraft_class_name == "net.minecraft.class_310"

@dataclass
class VersionInfo(VF):
    minescript_plus: str
    python_version: str
    mappings_installed: bool

def version_info():    
    print(VersionInfo(**asdict(ver_info()), minescript_plus=_ver, python_version=version, mappings_installed=True), file=stderr)

EventMode = Literal["flag", "callback"]
EventName = Literal["on_title", "on_subtitle", "on_actionbar", "on_open_screen"]
_events = {}


class EventDefinition:
    def __init__(self, name: str, mode: EventMode, flag: bool = False, condition: Callable | None = None, interval: float | None = None):
        self.name: str = name
        self.mode: EventMode = mode  # "flag" or "callback"
        self.flag: bool = flag
        self.condition: Callable = condition
        self.interval = interval

    def get_condition(self):
        if self.mode == "flag":
            return lambda: (self.flag, (), {})  # type: ignore
        elif self.mode == "callback":
            return self.condition
        else:
            raise ValueError(f"Invalid mode for event '{self.name}'.")

class Listener:
    def __init__(
        self,
        event_name: str,
        callback: Callable,
        condition_function: Callable,
        once: bool,
        manager,
        check_interval: float = 0.5,
    ):
        self.event_name: str = event_name
        self.callback: Callable = callback
        self.condition_function: Callable = condition_function
        self.once: bool = once
        self.manager = manager
        self.check_interval: float = check_interval
        self._running: bool = True
        self._task: asyncio.Task = None

    def start(self):
        self._task = asyncio.create_task(self.__run_loop())

    async def __run_loop(self):
        while self._running:
            triggered, args, kwargs = self.condition_function()
            if triggered:
                self.callback(*args, **kwargs)
                if self.once:
                    self.unregister()
            await asyncio.sleep(self.check_interval)

    def unregister(self):
        self._running = False
        self.manager._unregister(self)  # pylint: disable=W0212

class Event:
    _listeners = []
    _callbacks = {}

    @classmethod
    async def register(cls,
                        event_name: EventName | str,
                        callback: Callable[[], None],
                        once: bool = False,
                        check_interval: float = 0.05,
                        ) -> Listener:
        event_def = _events[event_name]
        condition = event_def.get_condition()
        event_interval = event_def.interval

        listener = Listener(
            event_name=event_name,
            callback=callback,
            condition_function=condition,
            once=once,
            manager=cls,
            check_interval=event_interval or check_interval
        )
        cls._listeners.append(listener)
        listener.start()
        return listener

    @classmethod
    def unregister(cls, listener: Listener):
        listener.unregister()

    @classmethod
    def _unregister(cls, listener: Listener):
        if listener in cls._listeners:
            cls._listeners.remove(listener)

    @classmethod
    def define_event(cls, event: EventDefinition):
        _events[event.name] = event

    @classmethod
    def define_flag_event(cls, name: str):
        cls.define_event(EventDefinition(name, mode="flag"))

    @classmethod
    def define_callback_event(cls, name: str, condition: Callable):
        cls.define_event(EventDefinition(
            name, mode="callback", condition=condition))

    @classmethod
    def event(cls, func: Callable) -> Callable:
        name = func.__name__
        cls._callbacks[name] = func
        return func

    @classmethod
    async def activate_all(cls):
        for name, func in cls._callbacks.items():
            await cls.register(name, func)
            
    @staticmethod
    def set_trigger(event_name: EventName | str, value: bool):
        event = _events.get(event_name)
        if not event or event.mode != "flag":
            raise ValueError(f"Event '{event_name}' is not of type flag.")
        event.flag = value


def __title_event_callback():
    r = Gui.get_title()
    if r is not None:
        return True, (r,), {}
    return False, (), {}

def __subtitle_event_callback():
    r = Gui.get_subtitle()
    if r is not None:
        return True, (r,), {}
    return False, (), {}

def __actionbar_event_callback():
    r = Gui.get_actionbar()
    if r is not None:
        return True, (r,), {}
    return False, (), {}

def __open_screen_event_callback():
    r = screen_name()
    if r is not None:
        return True, (r,), {}
    return False, (), {}

Event.define_event(EventDefinition(
    "on_title", mode="callback", condition=__title_event_callback))
Event.define_event(EventDefinition(
    "on_subtitle", mode="callback", condition=__subtitle_event_callback))
Event.define_event(EventDefinition(
    "on_actionbar", mode="callback", condition=__actionbar_event_callback))
Event.define_event(EventDefinition(
    "on_open_screen", mode="callback", condition=__open_screen_event_callback, interval=0.05))


class Keybind:
    def __init__(self) -> None:
        # Key map (int, GLFW code) -> (callback, name, category, description)
        self.keybinds: dict[int, tuple[Callable[[], None], str, str, str]] = {}
        self._listener_thread: threading.Thread = threading.Thread(
            target=self._key_listener_loop,
            daemon=True
        )
        self._listener_thread.start()

    def set_keybind(
        self,
        key: int,
        callback: Callable[[], None],
        name: str = "",
        category: str = "",
        description: str = ""
    ) -> None:
        self.keybinds[key] = (callback, name, category, description)

    def modify_keybind(
        self,
        key: int,
        callback: Callable[[], None],
        name: str = "",
        category: str = "",
        description: str = ""
    ) -> None:
        if key in self.keybinds:
            self.keybinds[key] = (callback, name, category, description)
        else:
            raise ValueError(f"[Keybind] No existing keybind for {key} to modify.")

    def remove_keybind(self, key: int) -> None:
        if key in self.keybinds:
            del self.keybinds[key]
        else:
            raise ValueError(f"[Keybind] No existing keybind for {key} to remove.")

    def _key_listener_loop(self) -> None:
        with EventQueue() as event_queue:
            event_queue.register_key_listener()
            while True:
                event = event_queue.get()
                if event.type == EventType.KEY:
                    key: int = event.key

                    if event.action == 0 and key in self.keybinds:
                        callback, *_ = self.keybinds[key]
                        try:
                            callback()
                        except Exception as e:
                            print(f"[Keybind] Error in callback for key {key}: {e}")

Array = JavaClass("java.lang.reflect.Array")
Clazz = JavaClass("java.lang.Class")
Float = JavaClass("java.lang.Float")
Minescript = JavaClass("net.minescript.common.Minescript")
Minecraft = JavaClass("net.minecraft.client.Minecraft")
ClickType = JavaClass("net.minecraft.world.inventory.ClickType")
Component = JavaClass("net.minecraft.network.chat.Component")
KeyMapping = JavaClass("net.minecraft.client.KeyMapping")
InputConstants = JavaClass("com.mojang.blaze3d.platform.InputConstants")
Difficulty = JavaClass("net.minecraft.world.Difficulty")
BlockPos = JavaClass("net.minecraft.core.BlockPos")
SoundEvents = JavaClass("net.minecraft.sounds.SoundEvents")
SoundSource = JavaClass("net.minecraft.sounds.SoundSource")
LightLayer = JavaClass("net.minecraft.world.level.LightLayer")

mappings = Minescript.mappingsLoader.get()
mc = Minecraft.getInstance()

mc.gui.setOverlayMessage(None, False)

"""
ClickType
Enum Constant   Description
CLONE           Clones the item in the slot.
PICKUP          Performs a normal slot click.
PICKUP_ALL      Replenishes the cursor stack with items from the screen handler.
QUICK_CRAFT     Drags items between multiple slots.
QUICK_MOVE      Performs a shift-click.
SWAP            Exchanges items between a slot and a hotbar slot.
THROW           Throws the item out of the inventory.
"""
    
def _get_private_field(clazz, field_name, super_class: bool=False): # type: ignore
    if super_class:
        c = clazz.getClass().getSuperclass()
    else:
        c = clazz.getClass()
    f = mappings.getRuntimeFieldName(c, field_name)
    field = c.getDeclaredField(f)
    field.setAccessible(True)
    return field.get(clazz)

def _call_private_method(clazz, intermediary: str):
    methods = clazz.getClass().getDeclaredMethods()
    for method in methods:
        if method.getName() == intermediary:
            method.setAccessible(True)
            parameter_type = Array.newInstance(Clazz, 0)
            return method.invoke(clazz, parameter_type)

def _set_grab_mouse():
    clazz = mc.mouseHandler
    field_name = "mouseGrabbed"
    c = clazz.getClass()
    f = mappings.getRuntimeFieldName(c, field_name)
    field = c.getDeclaredField(f)
    field.setAccessible(True)
    field.setBoolean(clazz, True)

def _check_fabric(clazz: str):
    if not fabric:
        print(f"Error: {clazz} class is only supported on Fabric")
        exit(1)
    
# # # INVENTORY # # #

class Inventory:
    @staticmethod
    def click_slot(slot: int, right_button: bool=False) -> bool:
        """
        Simulates a left (or right) mouse click on a specified inventory slot in the current screen.
        Args:
            slot (int): The index of the inventory slot to click (0-40).
            right_button (bool, optional): If True, simulates right click. Default: False
        Returns:
            bool: True if the click was performed successfully, False if no screen is open.
        """
        screen = mc.screen
        if screen is None:
            return False

        container_menu = screen.getMenu()
        mouse_button = 1 if right_button else 0
        # handleInventoryMouseClick(int syncId, int slotId, int button, ClickType arg3, Player arg4)
        mc.gameMode.handleInventoryMouseClick(
            container_menu.containerId, slot, mouse_button, ClickType.PICKUP, mc.player)

        return True

    @staticmethod
    def shift_click_slot(slot: int) -> bool:
        """
        Simulates a shift-click action on a specified inventory slot in the current screen.
        Args:
            slot (int): The index of the inventory slot to shift-click (0-40).
        Returns:
            bool: True if the shift-click action was performed successfully, False if no screen is open.
        Notes:
            This function interacts with the Minecraft game mode to perform a QUICK_MOVE (shift-click)
            action on the given slot. If there is no active screen, the function returns False.
        """
        screen = mc.screen
        if screen is None:
            return False

        container_menu = screen.getMenu()
        mouse_button = 0
        # handleInventoryMouseClick(int syncId, int slotId, int button, ClickType arg3, Player arg4)
        mc.gameMode.handleInventoryMouseClick(
            container_menu.containerId, slot, mouse_button, ClickType.QUICK_MOVE, mc.player)

        return True

    @staticmethod
    def inventory_hotbar_swap(inv_slot: int, hotbar_slot: int) -> bool:
        """
        Swaps an item between a specified inventory slot and a hotbar slot.
        Args:
            inv_slot (int): The index of the inventory slot to swap from (9-40).
            hotbar_slot (int): The index of the hotbar slot to swap with (0-8).
        Returns:
            bool: True if the swap action was initiated successfully, False if the screen is not available.
        Notes:
            This function interacts with the Minecraft client to perform the swap using the SWAP click type.
        """
        screen = mc.screen
        if screen is None:
            return False

        container_menu = screen.getMenu()
        # handleInventoryMouseClick(int syncId, int slotId, int button, ClickType arg3, Player arg4)
        mc.gameMode.handleInventoryMouseClick(
            container_menu.containerId, inv_slot, hotbar_slot, ClickType.SWAP, mc.player)

        return True

    @staticmethod
    def open_targeted_chest() -> bool:
        """
        Attempts to open the chest block currently targeted by the player.
        Works with any type of chest (single, double, trap, ender, etc.)
        Returns:
            bool: True if a chest was successfully opened, False otherwise.
        """
        block: TargetedBlock | None = player_get_targeted_block()
        if block is not None and "chest" not in block.type and "shulker_box" not in block.type:
            return False

        press_key_bind("key.use", True)
        r: bool = Screen.wait_screen()
        press_key_bind("key.use", False)

        return r

    @staticmethod
    def take_items(slots: list[int]) -> bool:
        """
        Transfers items from the specified inventory slots to the player's inventory using quick move.
        Args:
            slots (list[int]): A list of slot indices to move items from.
        Returns:
            bool: True if the operation was performed, False if no screen is open.
        """
        screen = mc.screen
        if screen is None:
            return False

        container_menu = screen.getMenu()
        mouse_button = 0
        for slot in slots:
            # handleInventoryMouseClick(int syncId, int slotId, int button, ClickType arg3, Player arg4)
            mc.gameMode.handleInventoryMouseClick(
                container_menu.containerId, slot, mouse_button, ClickType.QUICK_MOVE, mc.player)

        return True

    @staticmethod
    def find_item(item_id: str, cust_name: str = "", container: bool=False, try_open: bool=False) -> int | None:
        """
        Finds the first inventory slot containing a specific item, optionally by matching a custom name, and optionally by 
        searching an already opened container, or attempting to open a targeted one.
        Args:
            item_id (str): The ID of the item to search for.
            cust_name (str, optional): The custom name to match. If empty, only the item ID is considered. Defaults to "".
            container (bool, optional): If True, searches in the currently open container instead of the player's inventory. Defaults to False.
            try_open (bool, optional): If True and container is True, attempts to open the targeted chest before searching. Defaults to False.
        Returns:
            int | None: The slot ID of the first matching item, or None if not found.
        Notes:
            If try_open is True, then the function will close it after getting the items.
            Slot IDs:
                Player inventory: hotbar = 0-8, main = 9-35, offhand = 40, boots, leggins, chestplate, helmet = 36-39
                Single chest / Trap chest / Ender chest / Shulker box: 0-26
                Double chest: 0-53
                If you need to access the player's main inventory or hotbar with an open container, you must add the 
                container's size to the slot IDs. For example, if you have an open double chest, its size is 54 slots, 
                then the hotbar slots IDs will be from 0+54=54 to 8+54=62, and the main inventory will be from 9+54=63 
                to 35+54=89.
        """
        if not lib_nbt_module:
            print("Error: lib_nbt module not found.")
            echo_json([
                    {"text":"You can "},
                    {"text":"download it from here","underlined":True,"color":"#224488","click_event":{"action":"open_url","url":"https://minescript.net/sdm_downloads/lib_nbt-v1"},"hover_event":{"action":"show_text","value":"https://minescript.net/sdm_downloads/lib_nbt-v1"}},
                    {"text":", and put it in the "},
                    {"text":"/minescript","bold":True},
                    {"text":" folder."}
            ])
            return
            
        if not container:
            items: list[ItemStack] = player_inventory()
        else:
            if try_open:
                if not Inventory.open_targeted_chest():
                    return None
            items: list[ItemStack] = container_get_items()
            if try_open:
                Screen.close_screen()
        if items is None:
            #return None
            raise Exception("Error: You need an open container.") # pylint: disable=W0719
        
        fi = filter(lambda x: x.item == item_id, items)
        if cust_name == "":
            try:
                return next(fi).slot
            except StopIteration:
                return None

        for it in fi:
            nbt: dict = lib_nbt.parse_snbt(it.nbt)
            if "components" in nbt:
                comp = nbt.get("components")
                if "minecraft:custom_name" in comp:  # type: ignore
                    return it.slot

        return None

    @staticmethod
    def count_total(inventory: list[ItemStack], item_id: int) -> int:
        """
        Counts the total number of items with a specific item ID in the given inventory.

        Args:
            inventory (list[ItemStack]): A list of ItemStack objects representing the inventory.
            item_id (int): The ID of the item to count.

        Returns:
            int: The total count of items with the specified item ID in the inventory.
        """
        return sum(stack.count for stack in inventory if stack.item == item_id)

# # # SCREEN # # #

with render_loop:
    class Screen:
        @staticmethod
        def wait_screen(name: str = "", delay: int = 500) -> bool:
            """
            Waits for a screen with a specific name (or any screen if name is empty) to become available within a short period.

            Args:
                name (str, optional): The name of the screen to wait for. If empty, waits for any screen. Defaults to "".
                delay (int, optional): The maximum time to wait for the screen name in milliseconds. Defaults to 500.

            Returns:
                bool: True if the specified screen name (or any screen if name is empty) is detected 
                within the wait period, False otherwise.
            """
            w = 0.05
            i: int = int(delay * w) or 1
            for _ in range(i):
                scn_name = screen_name()
                if scn_name is not None:
                    if name == "":
                        return True
                    elif scn_name == name:
                        return True
                sleep(w)

            return False

        @staticmethod
        def close_screen() -> None:
            """
            Closes the currently open chest GUI in Minecraft
            
            Returns:
                None
            """
            screen = mc.screen
            if screen is not None:
                with render_loop:
                    container_id = screen.getMenu().containerId
                    mc.setScreen(None)
                    Client.send_packet("ServerboundContainerClosePacket", container_id)
                    _set_grab_mouse()

# # # GUI # # #

    class Gui:
        @staticmethod
        def get_title() -> str | None:
            """
            Retrieves the title

            Returns:
                str or None: The title, or None if not available.
            """
            title = _get_private_field(mc.gui, "title")
            if title is not None:
                title = title.tryCollapseToString()
            return title  # type: ignore

        @staticmethod
        def get_subtitle() -> str | None:
            """
            Retrieves the subtitle

            Returns:
                str or None: The subtitle, or None if not available.
            """
            subtitle = _get_private_field(mc.gui, "subtitle")
            if subtitle is not None:
                subtitle = subtitle.tryCollapseToString()
            return subtitle  # type: ignore

        @staticmethod
        def get_actionbar() -> str | None:
            """
            Retrieves and clears the current action bar (overlay message) string from the Minecraft GUI.

            Returns:
                str or None: The current overlay message string if present, otherwise None.
            """
            overlayMessageString = _get_private_field(mc.gui, "overlayMessageString")
            if overlayMessageString is not None:
                overlayMessageString = overlayMessageString.tryCollapseToString()
                mc.gui.setOverlayMessage(None, False)
            return overlayMessageString  # type: ignore

        @staticmethod
        def set_title(text: str) -> None:
            """
            Sets the title to the specified text.

            Args:
                text (str): The text to set as the title.

            Returns:
                None
            """
            mc.gui.setTitle(Component.literal(text))

        @staticmethod
        def set_subtitle(text: str) -> None:
            """
            Sets the subtitle to the specified text.

            Args:
                text (str): The text to set as the subtitle.

            Returns:
                None
            """
            mc.gui.setSubtitle(Component.literal(text))

        @staticmethod
        def set_actionbar(text: str, tinted: bool = False) -> None:
            """
            Sets the actionbar to the specified text.

            Args:
                text (str): The text to set as the actionbar.

            Returns:
                None
            """
            mc.gui.setOverlayMessage(Component.literal(text), tinted)

        @staticmethod
        def set_title_times(fadeInTicks: int, stayTicks: int, fadeOutTicks: int) -> None:
            """
            Sets the timing for the title and subtitle display.

            Args:
                fadeInTicks (int): Number of ticks for the title to fade in.
                stayTicks (int): Number of ticks for the title to stay visible.
                fadeOutTicks (int): Number of ticks for the title to fade out.

            Returns:
                None
            """
            mc.gui.setTimes(fadeInTicks, stayTicks, fadeOutTicks)

        @staticmethod
        def reset_title_times() -> None:
            """
            Resets the title and subtitle display times to the default values.

            Returns:
                None
            """
            mc.gui.resetTitleTimes()

        @staticmethod
        def clear_titles() -> None:
            """
            Clear the title and subtitle.

            Returns:
                None
            """
            mc.gui.clearTitles()
    # End render_loop

# # # KEY # # #

class Key:
    @staticmethod
    def __get_key_code(key_name: str):
        try:
            return InputConstants.getKey(key_name)
        except Exception:
            return InputConstants.UNKNOWN_KEY

    @staticmethod
    def __press_keybind(keybind, state: bool):
        if state:
            KeyMapping.click(keybind)
        KeyMapping.set(keybind, state)

    @staticmethod
    def press_key(key_name: str, state: bool):
        """
        Simulates pressing or releasing a key based on the provided key name and state.

        Args:
            key_name (str): The name of the key to press or release.
            state (bool): True to press the key, False to release it.

        Note:
            List of key codes used by Minecraft: https://minecraft.wiki/w/Key_codes#Current

        Returns:
            None
        """
        keybind = Key.__get_key_code(key_name)
        Key.__press_keybind(keybind, state)

# # # CLIENT # # #

class Client:
    @staticmethod
    def pause_game(pause_only: bool=False):
        mc.pauseGame(pause_only)
        
    @staticmethod
    def is_local_server() -> bool:
        """
        Retrieves if the server is running locally (is single player).

        Returns:
            bool: True if it's a local server, False otherwise.
        """
        return mc.isLocalServer() # type: ignore

    @staticmethod
    def is_multiplayer_server() -> bool:
        """
        Determines whether the current Minecraft instance is connected to a multiplayer server.

        Returns:
            bool: True if connected to a multiplayer server, False otherwise.
        """
        if fabric:
            return _call_private_method(mc, "method_31321") # type: ignore
        return _call_private_method(mc, "isMultiplayerServer") # type: ignore

    @staticmethod
    def disconnect():
        """
        Disconnects the current Minecraft network connection with a custom message.

        This function calls the network handler's disconnect method, passing a literal text message
        to indicate that the disconnection was initiated by the user.
        """
        mc.player.connection.getConnection().disconnect(
            Component.literal("Disconnected by user"))

    @staticmethod
    def get_options():
        """
        Returns an instance of the game options
        
        Use `Client.get_options().<option_name>().value` to get an option value.
        Use `Client.get_options().<option_name>().set(<value>)` to set an option value.
        Example: print("FOV:", Client.get_options().fov().value)
                 print("Gamma:", Client.get_options().gamma().get())
                 Client.get_options().fov().set(90)
        """
        return mc.options
    
    @staticmethod
    def send_packet(packet_class: str, *args, cat: str=""):
        # packet_class <- Intermediary name
        # Mojang: net.minecraft.network.protocol.game.<packet_class>
        # List: https://mappings.dev/1.21.8/net/minecraft/network/protocol/game/index.html
        # Yarn: net.minecraft.network.packet.c2s.play.<packet_class>
        # List: https://maven.fabricmc.net/docs/yarn-1.21.8+build.1/net/minecraft/network/packet/c2s/play/package-summary.html
        if packet_class.startswith("class"): # Intermediary
            packet_class = "net.minecraft." + packet_class
        elif "c2s" in packet_class:  # Yarn (Fabric)
            if cat == "":
                cat = "play"
            packet_class = f"net.minecraft.network.packet.c2s.{cat}.{packet_class}"
        else:   # Mojang
            if cat == "":
                cat = "game"
            packet_class = f"net.minecraft.network.protocol.{cat}.{packet_class}"
        p_class = JavaClass(packet_class)
        mc.player.connection.getConnection().send(p_class(*args))

# # # PLAYER # # #

class Player:
    @staticmethod
    def __get_player_info(name: str):
        return mc.player.connection.getPlayerInfo(name)

    @staticmethod
    def get_latency() -> int:
        name = player_name()
        return Player.__get_player_info(name).getLatency() # type: ignore

    @staticmethod
    def get_game_mode():
        """
        Retrieves the current game mode of the player.

        Returns:
            str: The game mode of the player as a string.
        """
        name = player_name()
        return Player.__get_player_info(name).getGameMode().getName()

    @staticmethod
    def is_creative() -> bool:
        """
        Checks if the player is in creative mode.

        Returns:
            bool: True if the player is in creative mode, False otherwise.
        """
        name = player_name()
        return Player.__get_player_info(name).getGameMode().isCreative() # type: ignore

    @staticmethod
    def is_survival() -> bool:
        """
        Checks if the player is in survival mode.

        Returns:
            bool: True if the player is in survival mode, False otherwise.
        """
        name = player_name()
        return Player.__get_player_info(name).getGameMode().isSurvival() # type: ignore

    @staticmethod
    def get_skin_url() -> str:
        """
        Retrieves the URL of the player's skin texture.

        Returns:
            str: The URL of the player's skin texture.
        """
        name = player_name()
        return Player.__get_player_info(name).getSkin().textureUrl() # type: ignore

    @staticmethod
    def get_food_level() -> float:
        """
        Retrieves the player's current food level.

        Returns:
            float: The current food level of the player.
        """
        foodStats = mc.player.getFoodData()
        return foodStats.getFoodLevel() # type: ignore
    
    @staticmethod
    def get_saturation_level() -> float:
        """
        Retrieves the player's current saturation level.

        Returns:
            float: The current saturation level of the player.
        """
        foodStats = mc.player.getFoodData()
        return foodStats.getSaturationLevel().value # type: ignore
    
    @staticmethod
    def get_player_block_position() -> list[int]:
        """
        Returns the player's current block position as a list of integers.

        This function retrieves the player's current position in the game world,
        rounds down each coordinate to the nearest integer using floor, and returns
        the resulting block-aligned position as a list.

        Returns:
            list of int: The [x, y, z] coordinates of the player's block position.
        """
        return [floor(p) for p in player_position()]

# # # SERVER # # #

class Server:
    @staticmethod
    def __get_server_data():
        return mc.player.connection.getServerData()

    @staticmethod
    def is_local() -> bool:
        """
        Determines if the server is running locally.

        Returns:
            bool: True if no server data is available (indicating a local server), False otherwise.
        """
        if Server.__get_server_data() is None:
            return True
        return False

    @staticmethod
    def get_ping() -> int | None:
        """
        Retrieves the ping value from the current server.

        Returns:
            int | None: The ping value if available, otherwise None.
        """
        server_data = Server.__get_server_data()
        if server_data is not None:
            return server_data.ping # type: ignore
        return None

    @staticmethod
    def is_lan() -> bool | None:
        """
        Determines if the server is running in LAN mode.

        Returns:
            bool | None: True if the server is running in LAN mode, False if not, 
            or None if server data is unavailable.
        """
        server_data = Server.__get_server_data()
        if server_data is not None:
            return server_data.isLan() # type: ignore
        return None
    
    @staticmethod
    def is_realm() -> bool | None:
        """
        Determines if the current server is a Realm.

        Returns:
            bool | None: True if the server is a Realm, False if not, or None if server data is unavailable.
        """
        server_data = Server.__get_server_data()
        if server_data is not None:
            return server_data.isRealm() # type: ignore
        return None
    
    @staticmethod
    def get_tablist() -> list[dict[str,Any]]:
        """
        Retrieves a list of dictionaries containing information about all online players in the tab list.
        Returns:
            list[dict[str, Any]]: A list where each dictionary represents a player and contains the following keys:
                - "Name" (str): The display name of the player in the tab list, or their profile name if not set.
                - "UUID" (Any): The unique identifier of the player.
                - "Latency" (Any): The player's network latency.
                - "GameMode" (str): The name of the player's current game mode.
                - "SkinURL" (str): The URL to the player's skin texture.
                - "TablistOrder" (Any): The player's order in the tab list.
                - "Team" (dict, optional): If the player is on a team, a dictionary with:
                    - "TeamName" (str): The display name of the team.
                    - "Color" (Any): The team's color.
        """
        op = []
        opi = {}
        opt = {}
        pi_list = mc.player.connection.getListedOnlinePlayers().toArray()
        for i in range(len(pi_list)):
            name = pi_list[i].getTabListDisplayName()
            if name is None or name == "":
                name = pi_list[i].getProfile().getName()
            else:
                name = name.getString()
            opi.update({
                "Name": name,
                "UUID": pi_list[i].getProfile().getId().toString(),
                "Latency": pi_list[i].getLatency(),
                "GameMode": pi_list[i].getGameMode().getName(),
                "SkinURL": pi_list[i].getSkin().textureUrl(),
                "TablistOrder": pi_list[i].getTabListOrder()
                })
            team = pi_list[i].getTeam()
            if team is not None:
                opt.update({
                    "TeamName": team.getDisplayName().getString(),
                    "Color": team.getColor().method_537()
                    })
                opi["Team"] = opt
            op.append(opi)
            
        return op

# # # WORLD # # #

class World:
    @staticmethod
    def __get_level_data():
        return mc.player.connection.getLevel().getLevelData()
    
    @staticmethod
    def is_raining() -> bool:
        """
        Checks if it is currently raining in the game world.

        Returns:
            bool: True if it is raining, False otherwise.
        """
        return World.__get_level_data().isRaining() # type: ignore

    @staticmethod
    def is_thundering() -> bool:
        """
        Checks if it is currently is_thundering in the game world.

        Returns:
            bool: True if it is is_thundering, False otherwise.
        """
        return World.__get_level_data().isThundering() # type: ignore

    @staticmethod
    def is_hardcore() -> bool:
        """
        Determines whether the current world is in hardcore mode.

        Returns:
            bool: True if the world is hardcore, False otherwise.
        """
        return World.__get_level_data().isHardcore() # type: ignore

    @staticmethod
    def get_difficulty() -> Difficulty: # type: ignore
        """
        Retrieves the current difficulty setting of the Minecraft world.

        Returns:
            Difficulty: The difficulty level of the current world.
        """
        return World.__get_level_data().getDifficulty()

    @staticmethod
    def get_spawn_pos(): # BlockPos
        """
        Retrieves the spawn position of the current level.

        Returns:
            BlockPos: The coordinates of the spawn position.
        """
        return World.__get_level_data().getSpawnPos()
    
    @staticmethod
    def get_game_time() -> int:
        """
        Returns the current game time in ticks.
        """
        return World.__get_level_data().getGameTime() # type: ignore
    
    @staticmethod
    def get_day_time() -> int:
        """
        Returns the current day time in ticks.
        """
        return World.__get_level_data().getDayTime() # type: ignore
   
    @staticmethod
    def get_targeted_sign_text() -> list[str] | None:
        """
        Retrieves the text from both the front and back sides of the sign block currently targeted by the player.
        
        Returns:
            list[str]: A list containing the text lines from the targeted sign. The first four elements are the lines from the front side, and the next four are from the back side.
        """
        position = player_get_targeted_block().position
        pos = BlockPos(*position)

        sign = mc.level.getBlockEntity(pos)
        if sign is None:
            return None
        
        sign_text = []
        
        # Front
        for i in range(0, 4):
            sign_text.append(sign.getText(True).getMessage(i, True).tryCollapseToString())
        # Back
        for i in range(0, 4):
            sign_text.append(sign.getText(False).getMessage(i, True).tryCollapseToString())
        
        return sign_text
        
    @staticmethod
    def find_nearest_entity(name_str: str="", type_str: str="") -> EntityData | None:
        """
        Finds the nearest entity matching the specified name and/or type.

        Args:
            name_str (str, optional): A substring to match in the entity's name. Defaults to "".
            type_str (str, optional): A substring to match in the entity's type. Defaults to "".

        Returns:
            EntityData | None: The nearest matching entity, or None if no entity is found.
        """
        name_str = f"(?=.*{name_str})" if name_str else ""
        name = rf"^(?!.*\b{player_name()}\b){name_str}.*"
        if type_str:
            el = entities(name=name, type=rf"(?=.*{type_str}).*", sort="nearest")
        else:
            el = entities(name=name, sort="nearest")
        return el[0] if len(el) > 0 else None

# # # TRADING # # #

class Trading:
    @staticmethod
    def get_offers():
        """
        Retrieves all merchant offers available in the current trading screen.
        Returns:
            MerchantOffers: The offers object, or None if no trading screen is open.
        """
        screen = mc.screen
        if screen is None:
            return None
        
        menu = screen.getMenu()
        offers = menu.getOffers()
        return offers
    
    @staticmethod
    def get_offer(offer_index: int):
        """
        Retrieves a specific merchant offer by index.
        Args:
            offer_index (int): The index of the offer.
        Returns:
            MerchantOffer: The offer object, or None if not available.
        """
        offers = Trading.get_offers()
        if offers is None:
            return None

        offer = offers.get(offer_index)
        return offer
        
    @staticmethod
    def get_costA(offer_index: int, name_and_count: bool=False) -> tuple[str, int] | ItemStack | None:
        """
        Gets the first cost item (costA) for a merchant offer.
        Args:
            offer_index (int): The offer index.
            name_and_count (bool, optional): If True, returns (name, count) tuple. Default: False
        Returns:
            tuple[str, int] | ItemStack | None: ItemStack or (name, count) tuple, or None if not available.
        """
        offer = Trading.get_offer(offer_index)
        if offer is None:
            return None
        
        item_stack = offer.getCostA()
        if name_and_count:
            return (item_stack.getItem().getName().getString(), item_stack.getCount()) # type: ignore
        return item_stack # type: ignore
    
    @staticmethod
    def get_costB(offer_index: int, name_and_count: bool=False) -> tuple[str, int] | ItemStack | None:
        """
        Gets the second cost item (costB) for a merchant offer.
        Args:
            offer_index (int): The offer index.
            name_and_count (bool, optional): If True, returns (name, count) tuple. Default: False
        Returns:
            tuple[str, int] | ItemStack | None: ItemStack or (name, count) tuple, or None if not available.
        """
        offer = Trading.get_offer(offer_index)
        if offer is None:
            return None
        
        item_stack = offer.getCostB()
        if name_and_count:
            return (item_stack.getItem().getName().getString(), item_stack.getCount()) # type: ignore
        return item_stack # type: ignore
    
    @staticmethod
    def get_result(offer_index: int, name_and_count: bool=False) -> tuple[str, int] | ItemStack | None:
        """
        Gets the result item for a merchant offer.
        Args:
            offer_index (int): The offer index.
            name_and_count (bool, optional): If True, returns (name, count) tuple. Default: False
        Returns:
            tuple[str, int] | ItemStack | None: ItemStack or (name, count) tuple, or None if not available.
        """
        offer = Trading.get_offer(offer_index)
        if offer is None:
            return None
        
        item_stack = offer.getResult()
        if name_and_count:
            return (item_stack.getItem().getName().getString(), item_stack.getCount()) # type: ignore
        return item_stack # type: ignore
    
    @staticmethod
    def trade_offer(offer_index: int):
        """
        Executes a trade for the specified merchant offer index.
        Args:
            offer_index (int): The index of the offer to trade.
        Returns:
            None if no trading screen is open.
        """
        screen = mc.screen
        if screen is None:
            return None
        
        menu = screen.getMenu()
        menu.setSelectionHint(offer_index)
        menu.tryMoveItems(offer_index)
        Client.send_packet("ServerboundSelectTradePacket", offer_index)
        
        mc.gameMode.handleInventoryMouseClick(
            menu.containerId, 2, 1, ClickType.QUICK_MOVE, mc.player)

# # # UTIL # # #

class Util:
    @staticmethod
    def get_job_id(cmd: str) -> int | None:
        """
        Returns the job_id of a job matching the given command string, or None if no such job exists.
        Args:
            cmd (str): The command string to search for among running jobs.
        Returns:
            int | None: The job_id of the matching job, or None if not found.
        """
        return ([job.job_id for job in job_info() if job.command == [cmd]] or [None])[0]

    @staticmethod
    def get_clipboard() -> str:
        """
        Retrieves the current contents of the system clipboard.

        Returns:
            str: The text currently stored in the clipboard.
        """
        return mc.keyboardHandler.getClipboard() # type: ignore

    @staticmethod
    def set_clipboard(string: str):
        """
        Sets the system clipboard to the specified string.

        Args:
            string (str): The text to be copied to the clipboard.
        """
        mc.keyboardHandler.setClipboard(string)

    @staticmethod
    def get_distance(pos1: list, pos2: list | None=None) -> float:
        """
        Calculates the Euclidean distance between two 3D positions.
        Args:
            pos1 (list): The first position as a list of three coordinates [x, y, z].
            pos2 (list, optional): The second position as a list of three coordinates [x, y, z].
                If None, defaults to the current player position.
        Returns:
            float: The Euclidean distance between pos1 and pos2.
        """
        if pos2 is None:
            pos2 = player_position()
        
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]

        return (dx**2 + dy**2 + dz**2)**0.5
    
    @staticmethod
    def get_nbt(obj: dict, path: str, default=None) -> Any:
        """
        Get a value from nested SNBT data using dot notation.
        
        Args:
            obj: Parsed SNBT object (dictionary)
            path: Dot-separated path (e.g., "Inventory.0.id")
            default: Default value if path not found
            
        Returns:
            Any: Value at the specified path or default
        """
        if not isinstance(obj, dict):
            return default
        
        current = obj
        parts = path.split('.')
        
        for part in parts:
            if isinstance(current, dict):
                if part in current:
                    current = current[part]
                else:
                    return default
            elif isinstance(current, list):
                try:
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return default
                except ValueError:
                    return default
            else:
                return default
        
        return current
        
    @staticmethod
    def get_light_level(block_pos=None, source: str="RAW") -> int: # type: ignore
        """
        Returns the light level at a specified block position in the Minecraft world.

        Args:
            block_pos (BlockPos, optional): The position of the block to check. If None, uses the player's current block position.
            source (str, optional): The type of light to retrieve. Can be "RAW" for raw brightness, "SKY" for sky light, or "BLOCK" for block light. Defaults to "RAW".

        Returns:
            int: The light level at the specified block position according to the selected source.
        """
        if block_pos is None:
            block_pos = mc.player.blockPosition()
        match source:
            case "RAW":
                return mc.level.getChunkSource().getLightEngine().getRawBrightness(block_pos, 0) # type: ignore
            case "SKY":
                return mc.level.getBrightness(LightLayer.SKY, block_pos) # type: ignore
            case "BLOCK":
                return mc.level.getBrightness(LightLayer.BLOCK, block_pos) # type: ignore
    
    @staticmethod
    def play_sound(sound=None, sound_source=None, volume: float=1.0, pitch: float=1.0):
        """
        Plays a sound on the client side.

            sound (optional): The sound event to play. Should be an instance from the SoundEvents class.
                Defaults to EXPERIENCE_ORB_PICKUP if None is provided.
            sound_source (optional): The source of the sound. Should be an instance from the SoundSource class.
                Defaults to PLAYERS if None is provided.
            volume (float, optional): The volume of the sound, clamped between 0.0 and 1.0. Defaults to 1.0.
            pitch (float, optional): The pitch of the sound, clamped between 0.0 and 2.0. Defaults to 1.0.
        """
        if sound is None:
            sound = SoundEvents.EXPERIENCE_ORB_PICKUP
        if sound_source is None:
            sound_source = SoundSource.PLAYERS
        volume = max(min(volume, 1), 0)
        pitch = max(min(pitch, 2), 0)
        mc.level.playLocalSound(mc.player, sound, sound_source, Float(volume), Float(pitch))

    @staticmethod
    def get_soundevents():
        """
        Returns SoundEvents class frmo Minecraft to get a sound for Util.play_sound() method.
        
        All sounds from this class here: https://mappings.dev/1.21.8/net/minecraft/sounds/SoundEvents.html
        """
        return SoundEvents

    @staticmethod
    def get_soundsource():
        """
        Returns SoundSource class frmo Minecraft to get a sound_source for Util.play_sound() method.
        
        All sounds from this class here: https://mappings.dev/1.21.8/net/minecraft/sounds/SoundSource.html
        """
        return SoundSource

# # # HUD # # #
if fabric:
    pyj_hud = eval_pyjinn_script(r"""
Minecraft = JavaClass("net.minecraft.client.Minecraft")
HudRenderCallback = JavaClass("net.fabricmc.fabric.api.client.rendering.v1.HudRenderCallback")
ARGB = JavaClass("net.minecraft.util.ARGB")
Component = JavaClass("net.minecraft.network.chat.Component")
ChatFormatting = JavaClass("net.minecraft.ChatFormatting")
BuiltInRegistries = JavaClass("net.minecraft.core.registries.BuiltInRegistries")
ResourceLocation = JavaClass("net.minecraft.resources.ResourceLocation")
ItemStack = JavaClass("net.minecraft.world.item.ItemStack")
Items = JavaClass("net.minecraft.world.item.Items")
Item = JavaClass("net.minecraft.world.item.Item")

mc = Minecraft.getInstance()

toggle_key = 301  # F12
tl = None
frames = 0
show = True
_texts: dict[int, tuple[bool, str, int, int, int, int, int, int, float, bool, bool, bool, bool, bool]] = {}
_ti: int = 0
_items: dict[int, tuple[bool, str, int, int, str, float]] = {}
_ii: int = 0

def _check_ver(ver: str) -> bool:
    _mc_ver = version_info().minecraft
    mc_version = [int(v) for v in _mc_ver.split(".")]
    ver = [int(v) for v in ver.split(".")]
    check = True
    for i in range(3):
        check = check and mc_version[i] >= ver[i]
    return check

def Float(number):
    return number.floatValue()

def render_item_count(gui_graphics, font, item_stack, scaled_X, scaled_Y, count):
    if item_stack.getCount() != 1 or count is not None:
        string2 = count if count is not None else str(item_stack.getCount())
        gui_graphics.drawString(font, string2, scaled_X + 19 - 2 - font.width(string2), scaled_Y + 6 + 3, -1, True)

def combine(*values):
  return values

def _add_text(*t):
    global _texts
    global _ti
    
    _texts[_ti] = tuple(t)
    _ti += 1
    return _ti - 1

def _update_text(index: int, *t):
    global _texts
    
    _texts[index] = tuple(t)

def _get_text_string(index: int):
    return _texts[index][1]
    
def _set_text_string(index: int, text: str):
    global _texts
    
    old = _texts[index]
    _texts[index] = combine(old[0], text, *old[2:])

def _get_text_position(index: int):
    return (_texts[index][2], _texts[index][3])

def _set_text_position(index: int, x: int, y: int):
    global _texts
    
    old = _texts[index]
    _texts[index] = combine(*old[:2], x, y, *old[4:])
    
def _remove_text(i):
    global _texts
    global _ti

    del _texts[i]
    _ti -= 1

def _clear_texts():
    global _texts
    
    _texts.clear()

def _get_texts():
    return _texts

def _show_hud(enable: bool):
    global show

    show = enable

def _show_text(index: int, enable: bool):
    global _texts
    
    old = _texts[index]
    _texts[index] = combine(enable, *old[1:])

def on_press_key(event):
    global show

    if event.action == 0 and event.key == toggle_key:
        show = not show

def _use_toggle_key(enable: bool):
    global tl
    
    if enable and tl is None:
            tl = add_event_listener("key", on_press_key)
    else:
        if tl is not None:
            remove_listener(tl)
            tl = None

def _set_toggle_key(tk: int):
    global toggle_key
    
    toggle_key = tk

def _get_item_from_itemid(item_id: str) -> Item:
    id = ResourceLocation.parse(item_id)
    return BuiltInRegistries.ITEM.getValue(id)

def _get_item_name(item: Item) -> str:
    return item.getName().getString()

def _add_item(*t):
    global _items
    global _ii
    
    _items[_ii] = tuple(t)
    _ii += 1
    return _ii - 1

def _update_item(index: int, *t):
    global _items
    
    _items[index] = tuple(t)

def _get_item_string(index: int):
    return _items[index][1]
    
def _set_item_string(index: int, text: str):
    global _items
    
    old = _items[index]
    _items[index] = combine(old[0], text, *old[2:])

def _get_item_position(index: int):
    return (_items[index][2], _items[index][3])

def _set_item_position(index: int, x: int, y: int):
    global _item
    
    old = _items[index]
    _items[index] = combine(*old[:2], x, y, *old[4:])

def _get_item_count(index: int):
    return _items[index][4]

def _set_item_count(index: int, count: str):
    global _item
    
    old = _items[index]
    _items[index] = combine(*old[:4], count, *old[5:])
        
def _remove_item(i):
    global _items
    global _ti

    del _items[i]
    _ii -= 1

def _clear_items():
    global _items
    
    _items.clear()
    
def _get_items():
    return _items

def _show_item(index: int, enable: bool):
    global _items
    
    old = _items[index]
    #_items[index] = (enable, *old[1:])
    #a, b, c, d, e = old[1:]
    #_items[index] = (enable, a, b, c, d, e)
    _items[index] = combine(enable, *old[1:])
    
def on_hud_render(guiGraphics, tickDeltaManager):
    global frames
    
    if not show:
        return
    
    for t in _texts:
        # _texts: dict[int, tuple[bool, str, int, int, int, int, int, int, float, bool, bool, bool, bool, bool]]
        state, text, x, y, r, g, b, alpha, scale, shadow, italic, underline, strikethrough, obfsucated = _texts[t]
        
        if state:
            styled_text = Component.literal(text)
            if italic:
                styled_text = styled_text.withStyle(ChatFormatting.ITALIC)
            if underline:
                styled_text = styled_text.withStyle(ChatFormatting.UNDERLINE)
            if strikethrough:
                styled_text = styled_text.withStyle(ChatFormatting.STRIKETHROUGH)
            if obfsucated:
                styled_text = styled_text.withStyle(ChatFormatting.OBFUSCATED)
            color: int = ARGB.color(alpha, r, g, b)
            
            scale = scale.floatValue()
            pose_stack = guiGraphics.pose()
            if _check_ver("1.21.6"):
                pose_stack.pushMatrix()
                pose_stack.scale(scale, scale)
            else:
                pose_stack.pushPose()
                pose_stack.scale(scale, scale, 0)
            scaled_X: int = int(x / scale)
            scaled_Y: int = int(y / scale)
            
            guiGraphics.drawString(mc.font, styled_text, scaled_X, scaled_Y, color, shadow)
            
            if _check_ver("1.21.6"):
                pose_stack.popMatrix()
            else:
                pose_stack.popPose()
    
    for i in _items:
        state, item_id, x, y, count, scale = _items[i]
        
        if state:
            scale = scale.floatValue()
            pose_stack = guiGraphics.pose()
            if _check_ver("1.21.6"):
                pose_stack.pushMatrix()
                pose_stack.scale(scale, scale)
            else:
                pose_stack.pushPose()
                pose_stack.scale(scale, scale, 0)
            scaled_X: int = int(x / scale)
            scaled_Y: int = int(y / scale)
            
            item = _get_item_from_itemid(item_id)
            item_stack = ItemStack(item)
            
            guiGraphics.renderItem(item_stack, scaled_X, scaled_Y)
            if count != "":
                render_item_count(guiGraphics, mc.font, item_stack, scaled_X, scaled_Y, count)
            
            if _check_ver("1.21.6"):
                pose_stack.popMatrix()
            else:
                pose_stack.popPose()


callback = ManagedCallback(on_hud_render)
HudRenderCallback.EVENT.register(HudRenderCallback(callback))

    """)

    _add_text = pyj_hud.get("_add_text")
    _update_text = pyj_hud.get("_update_text")
    _get_text_string = pyj_hud.get("_get_text_string")
    _set_text_string = pyj_hud.get("_set_text_string")
    _get_text_position = pyj_hud.get("_get_text_position")
    _set_text_position = pyj_hud.get("_set_text_position")
    _remove_text = pyj_hud.get("_remove_text")
    _clear_texts = pyj_hud.get("_clear_texts")
    _get_texts = pyj_hud.get("_get_texts")
    _show_hud = pyj_hud.get("_show_hud")
    _show_text = pyj_hud.get("_show_text")
    _use_toggle_key = pyj_hud.get("_use_toggle_key")
    _set_toggle_key = pyj_hud.get("_set_toggle_key")
    _get_item_from_itemid = pyj_hud.get("_get_item_from_itemid")
    _get_item_name = pyj_hud.get("_get_item_name")
    _add_item = pyj_hud.get("_add_item")
    _update_item = pyj_hud.get("_update_item")
    _get_item_string = pyj_hud.get("_get_item_string")
    _set_item_string = pyj_hud.get("_set_item_string")
    _get_item_position = pyj_hud.get("_get_item_position")
    _set_item_position = pyj_hud.get("_set_item_position")
    _get_item_count = pyj_hud.get("_get_item_count")
    _set_item_count = pyj_hud.get("_set_item_count")
    _remove_item = pyj_hud.get("_remove_item")
    _clear_items = pyj_hud.get("_clear_items")
    _get_items = pyj_hud.get("_get_items")
    _show_item = pyj_hud.get("_show_item")

class Hud:    
    @staticmethod
    def add_text(text: str, x: int, y: int, color: tuple=(255,255,255), alpha: int=255, scale: float=1.0, 
        shadow: bool=False, italic: bool=False, underline: bool=False, strikethrough: bool=False, obfsucated: bool=False) -> int:
        """
        Adds a text string to the Minecraft HUD at the specified position.
        Args:
            text (str): The text to display.
            x (int): X position on screen.
            y (int): Y position on screen.
            color (tuple, optional): RGB color tuple. Default: (255,255,255)
            alpha (int, optional): Alpha transparency. Default: 255
            scale (float, optional): Text scale. Default: 1.0
            shadow, italic, underline, strikethrough, obfsucated (bool, optional): Text effects.
        Returns:
            int: Index of the added text.
        """
        _check_fabric("Hud")
        return _add_text(True, text, x, y, *color, alpha, scale, shadow, italic, underline, strikethrough, obfsucated) # type: ignore

    @staticmethod
    def update_text(index: int, text: str, x: int, y: int, color: tuple=(255,255,255), alpha: int=255, scale: float=1.0, 
        shadow: bool=False, italic: bool=False, underline: bool=False, strikethrough: bool=False, obfsucated: bool=False):
        """
        Updates a text string to the Minecraft HUD at the specified position.
        Args:
            index (int): Index of the text to update.
            text (str): The text to display.
            x (int): X position on screen.
            y (int): Y position on screen.
            color (tuple, optional): RGB color tuple. Default: (255,255,255)
            alpha (int, optional): Alpha transparency. Default: 255
            scale (float, optional): Text scale. Default: 1.0
            shadow, italic, underline, strikethrough, obfsucated (bool, optional): Text effects.
        Returns:
            int: Index of the added text.
        """
        _check_fabric("Hud")
        _update_text(index, True, text, x, y, *color, alpha, scale, shadow, italic, underline, strikethrough, obfsucated)

    @staticmethod
    def get_text_string(index: int) -> str:
        """
        Returns the position of an existing entry by its index.
        Args:
            index (int): Index of the text to change.
        Returns:
            str: Current text.
        """
        _check_fabric("Hud")
        return _get_text_string(index) # type: ignore
        
    @staticmethod
    def set_text_string(index: int, text: str):
        """
        Change the text of an existing entry by its index.
        Args:
            index (int): Index of the text to change.
            text (str): New text
        """
        _check_fabric("Hud")
        _set_text_string(index, text)
        
    @staticmethod
    def get_text_position(index: int) -> tuple[int, int]:
        """
        Returns the position of an existing entry by its index.
        Args:
            index (int): Index of the text to change.
        Returns:
            tuple: Position in x and y coordinates.
        """
        _check_fabric("Hud")
        return _get_text_position(index) # type: ignore
        
    @staticmethod
    def set_text_position(index: int, x: int, y: int):
        """
        Change the position of an existing entry by its index.
        Args:
            index (int): Index of the text to change.
            x (int): X position on screen.
            y (int): Y position on screen.
        """
        _check_fabric("Hud")
        _set_text_position(index, x, y)

    @staticmethod
    def remove_text(index: int):
        """
        Removes a text entry from the HUD by its index.
        Args:
            index (int): Index of the text to remove.
        """
        _check_fabric("Hud")
        _remove_text(index)
    
    @staticmethod
    def clear_texts():
        """
        Removes all texts entries from the HUD.
        """
        _check_fabric("Hud")
        _clear_texts()
    
    @staticmethod
    def get_texts() -> dict[int, tuple[bool, str, int, int, int, int, int, int, float, bool, bool, bool, bool, bool]]:
        """
        Returns all HUD text entries and their properties.
        Returns:
            dict: Mapping of index to text properties.
        """
        _check_fabric("Hud")
        return _get_texts() # type: ignore

    @staticmethod
    def show_hud(enable: bool):
        """
        Enables or disables display of all HUD content.
        Args:
            enable (bool): True to show, False to hide.
        """
        _check_fabric("Hud")
        _show_hud(enable)

    @staticmethod
    def show_text(index: int, enable: bool):
        """
        Shows or hides a specific HUD text entry.
        Args:
            index (int): Index of the text.
            enable (bool): True to show, False to hide.
        """
        _check_fabric("Hud")
        _show_text(index, enable)

    @staticmethod
    def use_toggle_key(enable: bool):
        """
        Enables or disables the HUD toggle key (default F12).
        Args:
            enable (bool): True to allow toggling HUD with key.
        """
        _check_fabric("Hud")
        _use_toggle_key(enable)

    @staticmethod
    def set_toggle_key(toggle_key: int):
        """
        Sets the key code used to toggle HUD display (GLFW key code).
        Args:
            toggle_key (int): GLFW key code to use for toggling.
        """
        _check_fabric("Hud")
        _set_toggle_key(toggle_key)

    @staticmethod
    def get_item_from_itemid(item_id: str):
        """
        Gets the item object from its item ID string.
        Args:
            item_id (str): The item ID.
        Returns:
            Item: The item object.
        """
        _check_fabric("Hud")
        return _get_item_from_itemid(item_id)
    
    @staticmethod
    def get_itemid_from_block_type(block_type: str) -> str:
        """
        Extracts the item ID from a block type string.
        Args:
            block_type (str): The block type string.
        Returns:
            str: The item ID.
        """
        _check_fabric("Hud")
        return block_type.split(r"\[")[0]
    
    @staticmethod
    def get_item_name(item) -> str:
        """
        Gets the display name of an item.
        Args:
            item: The item object.
        Returns:
            str: The item name.
        """
        _check_fabric("Hud")
        return _get_item_name(item) # type: ignore
    
    @staticmethod
    def add_item(item_id: str, x: int, y: int, count: str="", scale: float=1.0) -> int:
        """
        Adds an item icon to the HUD at the specified position.
        Args:
            item_id (str): The item ID to display.
            x (int): X position on screen.
            y (int): Y position on screen.
            count (str, optional): Text to show as item count. Default: ""
            scale (float, optional): Icon scale. Default: 1.0
        Returns:
            int: Index of the added item.
        """
        _check_fabric("Hud")
        return _add_item(True, item_id, x, y, count, scale) # type: ignore
    
    @staticmethod
    def update_item(index: int, item_id: str, x: int, y: int, count: str="", scale: float=1.0):
        """
        Adds an item icon to the HUD at the specified position.
        Args:
            index (int): Index of the item to update.
            item_id (str): The item ID to display.
            x (int): X position on screen.
            y (int): Y position on screen.
            count (str, optional): Text to show as item count. Default: ""
            scale (float, optional): Icon scale. Default: 1.0
        """
        _check_fabric("Hud")
        _update_item(True, item_id, x, y, count, scale)

    @staticmethod
    def get_item_string(index: int) -> str:
        """
        Returns the position of an existing entry by its index.
        Args:
            index (int): Index of the item to change.
        Returns:
            str: Current item.
        """
        _check_fabric("Hud")
        return _get_item_string(index) # type: ignore
        
    @staticmethod
    def set_item_string(index: int, item: str):
        """
        Change the item of an existing entry by its index.
        Args:
            index (int): Index of the item to change.
            item (str): New item
        """
        _check_fabric("Hud")
        _set_item_string(index, item)
        
    @staticmethod
    def get_item_position(index: int) -> tuple[int, int]:
        """
        Returns the position of an existing entry by its index.
        Args:
            index (int): Index of the item to change.
        Returns:
            tuple: Position in x and y coordinates.
        """
        _check_fabric("Hud")
        return _get_item_position(index) # type: ignore
        
    @staticmethod
    def set_item_position(index: int, x: int, y: int):
        """
        Change the position of an existing entry by its index.
        Args:
            index (int): Index of the item to change.
            x (int): X position on screen.
            y (int): Y position on screen.
        """
        _check_fabric("Hud")
        _set_item_position(index, x, y)
        
    @staticmethod
    def get_item_count(index: int) -> int:
        """
        Returns the count of an existing entry by its index.
        Args:
            index (int): Index of the item to change.
        Returns:
            str: Current display count
        """
        _check_fabric("Hud")
        return _get_item_count(index) # type: ignore
        
    @staticmethod
    def set_item_count(index: int, count: str):
        """
        Change the count of an existing entry by its index.
        Args:
            index (int): Index of the item to change.
            count (str): Count to display for this item.
        """
        _check_fabric("Hud")
        _set_item_count(index, count)

    @staticmethod
    def remove_item(index: int):
        """
        Removes an item entry from the HUD by its index.
        Args:
            index (int): Index of the item to remove.
        """
        _check_fabric("Hud")
        _remove_item(index)
    
    @staticmethod
    def clear_items():
        """
        Removes all items entries from the HUD.
        """
        _check_fabric("Hud")
        _clear_items()
        
    @staticmethod
    def get_items() -> dict[int, tuple[bool, str, int, int, str, float]]:
        """
        Returns all HUD item entries and their properties.
        Returns:
            dict: Mapping of index to item properties.
        """
        _check_fabric("Hud")
        return _get_items() # type: ignore

    @staticmethod
    def show_item(index: int, enable: bool):
        """
        Shows or hides a specific HUD item entry.
        Args:
            index (int): Index of the item.
            enable (bool): True to show, False to hide.
        """
        _check_fabric("Hud")
        _show_item(index, enable)
