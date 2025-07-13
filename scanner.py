"""
    @author RazrCraft
    @create date 2025-06-17 18:34:53
    @modify date 2025-06-23 04:48:33
    @desc A really simple (and perhaps buggy) scanner script that indicates at what coordinates it's discovering certain 
          blocks (configurable) in a 64 blocks radius of the player (also configurable), displaying a chat message for every 
          block (only once).
          Run the script to start the service, and then, to activate the scanner and display what it finds, you have to 
          press "*" key. This key bind toggle (pause/unpause) the scanner. And "-" key stops the service (terminates the 
          script). Both key binds are configurable too.
 """
import queue
from time import sleep
import types
from minescript import EventQueue, EventType, BlockPack, script_loop, echo_json, player_position
from lib_blockpack_parser import BlockPackParser

# Key binds (For other values, look here: https://www.glfw.org/docs/3.4/group__keys.html)
KEY = types.SimpleNamespace()
KEY.TOGGLE = 332    # *
KEY.STOP = 333      # -

# Block IDs to search for
target_blocks = {
    "minecraft:end_portal_frame",
    "minecraft:infested_stone_bricks",
    "minecraft:infested_cobblestone",
    "minecraft:infested_mossy_stone_bricks",
    "minecraft:suspicious_gravel",
    "minecraft:suspicious_sand",
    "minecraft:decorated_pot",
    "minecraft:mud_bricks",
    "minecraft:terracotta",
    "minecraft:cobbled_deepslate",
    "minecraft:chest",
    "minecraft:shulker_box"
}

radius = 64
toggle = False
blks = set()

echo_json('[{"text":"Scanner Service started.", "color":"gold"}]')

with EventQueue() as event_queue:
    event_queue.register_key_listener()
    while True:
        try:
            if event_queue.queue.not_empty:
                event = event_queue.get(block=False, timeout=1)
                if event.type == EventType.KEY and event.action == 0:
                    match event.key:
                        case KEY.TOGGLE:
                            toggle = not toggle
                            if toggle:
                                echo_json('[{"text":"Scanner ", "color":"white"}, {"text":"ON", "color":"green"}]')
                            else:
                                echo_json('[{"text":"Scanner ", "color":"white"}, {"text":"OFF", "color":"red"}]')
                        case KEY.STOP:
                            echo_json('[{"text":"Stopping Scanner Service...", "color":"gold"}]')
                            break
        except queue.Empty:
            pass
                
        if toggle:
            with script_loop:
                pos = player_position()
                x = round(pos[0])
                y = round(pos[1])
                z = round(pos[2])

                blockpack = BlockPack.read_world((x-radius, y-radius, z-radius), (x+radius, y+radius, z+radius))
                parser = BlockPackParser.parse_blockpack(blockpack)

                for tile in parser.tiles:
                    for pos, block in tile.iter_setblock_params(): # type: ignore
                        blk = parser.palette[block]
                        if any(blk.startswith(b) for b in target_blocks):
                            if pos not in blks:
                                #echo(f" {blk} @ {pos}")
                                echo_json('[{"text":"' + blk + ' ", "color":"gray"}, {"text":"' + str(pos) + '", "color":"blue"}]')
                                blks.add(pos)

        sleep(.1)
