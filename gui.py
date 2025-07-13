"""
    @author RazrCraft
    @create date 2025-07-08 14:10:09
    @modify date 2025-07-08 14:26:12
    @desc Simple GUI for testing the lib_screen library
 """
from minescript import execute
from lib_screen import Screen
from minescript_plus import get_job_id

gui = Screen("Minescript GUI", 240, 120)

def button_on_click(idx: int):
    match idx:
        case 0:
            job_name = gui.input_dialog(" ", "Kill job by name: ")
            job_id = get_job_id(job_name)
            if job_id is not None:
                execute(f"\\killjob {job_id}")
        case 1:
            ...

button1 = gui.add_button(on_click=lambda: button_on_click(0), text="Button 1")
button1.x = 5
button1.y = 5
button2 = gui.add_button(on_click=lambda: button_on_click(1), text="Button 2", right=button1)
button3 = gui.add_button(on_click=lambda: button_on_click(2), text="Button 3", down=button1)
button4 = gui.add_button(on_click=lambda: button_on_click(3), text="Button 4", right=button3)
button5 = gui.add_button(on_click=lambda: button_on_click(4), text="Button 5", down=button3)
button6 = gui.add_button(on_click=lambda: button_on_click(5), text="Button 6", right=button5)
button7 = gui.add_button(on_click=lambda: button_on_click(6), text="Button 7", down=button5)
button8 = gui.add_button(on_click=lambda: button_on_click(7), text="Button 8", right=button7)

# Show screen
gui.show()
