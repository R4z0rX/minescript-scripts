"""
    Minescript Plus
    Version: 0.8-alpha
    Author: RazrCraft
    Date: 2025-07-16

    User-friendly API for scripts that adds extra functionality to the
    Minescript mod, using lib_java and other libraries.
    This module should be imported by other scripts and not run directly.

    Usage: Similar to Minescript, import minescript_plus  # from Python script
    
    Note: Some code shared by @maxuser (Minescript's creator) on the 
    official discord was used in this API, mostly in the Inventory class.
"""
import asyncio
from time import sleep
from typing import Callable, Literal
from minescript import (set_default_executor, script_loop, render_loop, ItemStack, TargetedBlock, version_info, player_inventory,
                        player_get_targeted_block, press_key_bind, screen_name, player_name, job_info,
                        container_get_items)
from lib_java import JavaClass, java_class_map, java_member_map
import lib_nbt

set_default_executor(script_loop)
EventMode = Literal["flag", "callback"]
EventName = Literal["on_title", "on_subtitle", "on_actionbar"]
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

# Mojang -> Intermediary mappings
mc_class_name = version_info().minecraft_class_name
if mc_class_name == "net.minecraft.class_310":
    java_class_map.update({
        "net.minecraft.client.Minecraft": "net.minecraft.class_310",                # net.minecraft.client.MinecraftClient
        "net.minecraft.world.inventory.ClickType": "net.minecraft.class_1713",      # net.minecraft.screen.slot.SlotActionType
        "net.minecraft.network.chat.Component": "net.minecraft.class_2561",         # net.minecraft.network.chat.Text
        "net.minecraft.client.KeyMapping": "net.minecraft.class_304",               # net.minecraft.client.option.KeyBinding
        "com.mojang.blaze3d.platform.InputConstants": "net.minecraft.class_3675",   # net.minecraft.client.util.InputUtil
        "net.minecraft.world.Difficulty": "net.minecraft.class_1267"
    })
    java_member_map.update({
        "getInstance": "method_1551",
        "getNetworkHandler": "method_1562",
        "getConnection": "method_48296",
        "disconnect": "method_10747",
        "name": "field_3752",
        "ip": "field_3761",
        "status": "field_3753",  # playerCountLabel
        "motd": "field_3757",
        "ping": "field_3758",
        "protocol": "field_3756",
        "version": "field_3760",
        "playerList": "field_3762",
        "pauseGame": "method_20539", # openGameMenu
        "isLocalServer": "method_1542", # isInSingleplayer
        "isLan": "method_2994",
        "isRealm": "method_52811",
        "getLatency": "method_2959",
        "getGameMode": "method_2958",
        "getName": "method_8381",
        "isCreative": "method_8386",
        "isSurvival": "method_8388",
        "getLevel":"method_2890", # getWorld
        "getLevelData": "method_28104", # getLevelProperties
        "isRaining": "method_156",
        "isThundering": "method_203",
        "isHardcore": "method_152",
        "getDifficulty": "method_207",
        "getSpawnPos": "method_56126",
        "getGameTime": "method_188", # getTime
        "getDayTime": "method_217", # getTimeOfDay
        "player": "field_1724",
        "screen": "field_1755",
        "gui": "field_1705",
        "gameMode": "field_1761",
        "handleInventoryMouseClick": "method_2906",
        "getMenu": "method_17577",
        "containerId": "field_7763",
        "keyPressed": "method_25404",
        "quickMoveStack": "method_7601",
        "literal": "method_43470",
        "title": "field_2016",
        "subtitle": "field_2039",
        "tryCollapseToString": "method_54160",  # getLiteralString()
        "setTitle": "method_34004",             # setTitle(Text title)
        "setSubtitle": "method_34002",          # setSubtitle(Text subtitle)
        "setTimes": "method_34001",             # setTitleTicks(int fadeInTicks, int stayTicks, int fadeOutTicks)
        "resetTitleTimes": "method_1742",       # setDefaultTitleFade()
        "clearTitles": "method_34003",          # clearTitle()
        "setOverlayMessage": "method_1758",     # Gui.setOverlayMessage(Text message, boolean tinted)               # Actionbar
        "overlayMessageString": "field_2018",   # overlayMessage # Actionbar
        "getTabList": "method_1750",            # getPlayerListHud()
        "getPlayerInfos": "method_48213",       # collectPlayerEntries()                                            #  TabList
        "getOnlinePlayers": "method_2880",      # getPlayerList()
        "getListedOnlinePlayers": "method_45732",  # getListedPlayerListEntries()
        "getPlayerInfo": "method_2874",         # getPlayerListEntry(String profileName)
        "getSkin": "method_52810",              # getSkinTextures()
        "textureUrl": "comp_1911",
        "getServerData": "method_45734",        # getServerInfo() 
        "click": "method_1420",                 # onKeyPressed(InputUtil$Key key)
        "set": "method_1416",                   # setKeyPressed(InputUtil$Key key, boolean pressed)
        "getKey": "method_15981",               # fromTranslationKey(String translationKey)
        "UNKNOWN": "field_16237",               # UNKNOWN_KEY
        "getFoodData": "method_7344",           # getHungerManager
        "getFoodLevel": "method_7586",
        "setFoodLevel": "method_7580",
        "getSaturationLevel": "method_7589",
        "setSaturation": "method_7581"
    })

Minecraft = JavaClass("net.minecraft.client.Minecraft")
ClickType = JavaClass("net.minecraft.world.inventory.ClickType")
Component = JavaClass("net.minecraft.network.chat.Component")
KeyMapping = JavaClass("net.minecraft.client.KeyMapping")
InputConstants = JavaClass("com.mojang.blaze3d.platform.InputConstants")
Difficulty = JavaClass("net.minecraft.world.Difficulty")

mc = Minecraft.getInstance()

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

# # # INVENTORY # # #

class Inventory:
    @staticmethod
    def click_slot(slot: int) -> bool:
        """
        Simulates a left mouse click on a specified inventory slot in the current screen.
        Args:
            slot (int): The index of the inventory slot to click (0-40).
        Returns:
            bool: True if the click was performed successfully, False if no screen is open.
        """
        screen = mc.screen
        if screen is None:
            return False

        container_menu = screen.getMenu()
        mouse_button = 0
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

# # # SCREEN # # #

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
        Closes the currently open chest GUI in Minecraft by simulating an Escape key press.
        Returns:
            None
        """
        screen = mc.screen
        if screen is not None:
            # keyPressed(int keyCode, int scanCode, int modifiers)
            screen.keyPressed(256, 0, 0)  # 256 is key code for escape key.

# # # GUI # # #

with render_loop:
    class Gui:
        @staticmethod
        def get_title() -> str | None:
            """
            Retrieves the title

            Returns:
                str or None: The title, or None if not available.
            """
            c = mc.gui.getClass()
            f = java_member_map.get("title")
            field = c.getDeclaredField(f)
            field.setAccessible(True)
            title = field.get(mc.gui)
            if title is not None:
                # title = title.getString()
                title = title.tryCollapseToString()
            return title  # type: ignore

        @staticmethod
        def get_subtitle() -> str | None:
            """
            Retrieves the subtitle

            Returns:
                str or None: The subtitle, or None if not available.
            """
            c = mc.gui.getClass()
            f = java_member_map.get("subtitle")
            field = c.getDeclaredField(f)
            field.setAccessible(True)
            subtitle = field.get(mc.gui)
            if subtitle is not None:
                # subtitle = subtitle.getString()
                subtitle = subtitle.tryCollapseToString()
            return subtitle  # type: ignore

        @staticmethod
        def get_actionbar() -> str | None:
            """
            Retrieves and clears the current action bar (overlay message) string from the Minecraft GUI.

            Returns:
                str or None: The current overlay message string if present, otherwise None.
            """
            c = mc.gui.getClass()
            f = java_member_map.get("overlayMessageString")
            field = c.getDeclaredField(f)
            field.setAccessible(True)
            overlayMessageString = field.get(mc.gui)
            if overlayMessageString is not None:
                # overlayMessageString = overlayMessageString.getString()
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
    def disconnect():
        """
        Disconnects the current Minecraft network connection with a custom message.

        This function calls the network handler's disconnect method, passing a literal text message
        to indicate that the disconnection was initiated by the user.
        """
        mc.getNetworkHandler().getConnection().disconnect(
            Component.literal("Disconnected by user"))

# # # PLAYER # # #

class Player:
    @staticmethod
    def __get_player_info(name: str):
        return mc.getNetworkHandler().getPlayerInfo(name)

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
        foodStats = mc.player.getFoodData()
        return foodStats.getFoodLevel() # type: ignore
    
    @staticmethod
    def get_saturation_level() -> float:
        foodStats = mc.player.getFoodData()
        return foodStats.getSaturationLevel().value # type: ignore

# # # SERVER # # #

class Server:
    @staticmethod
    def __get_server_data():
        return mc.getNetworkHandler().getServerData()

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

# # # WORLD # # #

class World:
    @staticmethod
    def __get_level_data():
        return mc.getNetworkHandler().getLevel().getLevelData()
    
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
