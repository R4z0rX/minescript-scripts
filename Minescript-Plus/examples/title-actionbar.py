"""
    @author RazrCraft
    @create date 2025-06-25 01:55:12
    @modify date 2025-08-11 18:19:40
    @desc Title, subtitle, and actionbar example
 """
from time import sleep
from minescript_plus import Gui

print(f"{Gui.get_actionbar() = }")
print(f"{Gui.get_title() = }")
print(f"{Gui.get_subtitle() = }")
Gui.set_actionbar("ACTIONBAR", False)
sleep(2)
print(f"{Gui.get_actionbar() = }")
# setTimes(int fadeInTicks, int stayTicks, int fadeOutTicks)
Gui.set_title_times(30, 20, 30)
Gui.set_title("This is a Title")
Gui.set_subtitle("This is a Subtitle")
print(f"{Gui.get_title() = }")
print(f"{Gui.get_subtitle() = }")
sleep(1)
Gui.reset_title_times()
Gui.set_actionbar("TINTED ACTIONBAR", True)
sleep(2)
print(f"{Gui.get_actionbar() = }")
Gui.set_title("Clear this Title")
Gui.set_subtitle("Clear this Subtitle")
sleep(.5)
Gui.clear_titles()
print(f"{Gui.get_title() = }")
print(f"{Gui.get_subtitle() = }")
print(f"{Gui.get_actionbar() = }")
