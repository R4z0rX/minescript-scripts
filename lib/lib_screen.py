"""
    @author RazrCraft
    @create date 2025-07-05 07:58:44
    @modify date 2025-07-05 17:57:52
    @desc A helper library for creating simple screens with Tkinter
 """
# pylint: disable=W0238
import tkinter as tk
from tkinter import simpledialog
from typing import Callable


class ButtonWidget:
    def __init__(self, root, on_click: Callable, text: str, width: int, height: int, x: int, y: int):
        self.__btn = tk.Button(root, text=text, width=width, height=1, command=on_click)
        self.__btn.place(x=x, y=y, width=width, height=height)
        self.__on_click = on_click
        self.__text = text
        self.__width = self.__btn.winfo_reqwidth()
        self.__height = height
        self.__x = x
        self.__y = y

    @property
    def text(self):
        return self.__btn['text']
    @text.setter
    def text(self, value):
        self.__btn['text'] = value
        self.__text = value

    @property
    def width(self):
        return self.__width
    @width.setter
    def width(self, value):
        self.__width = value
        self.__btn.place_configure(width=value)

    @property
    def height(self):
        return self.__height
    @height.setter
    def height(self, value):
        self.__height = value
        self.__btn.place_configure(height=value)

    @property
    def x(self):
        return self.__x
    @x.setter
    def x(self, value):
        self.__x = value
        self.__btn.place_configure(x=value)

    @property
    def y(self):
        return self.__y
    @y.setter
    def y(self, value):
        self.__y = value
        self.__btn.place_configure(y=value)

    def remove(self):
        self.__btn.destroy()

class TextInputWidget:
    def __init__(self, root, on_change: Callable, text: str, width: int, height: int, x: int, y: int):
        self.__var = tk.StringVar(value=text)
        self.__entry = tk.Entry(root, textvariable=self.__var, width=width)
        self.__entry.place(x=x, y=y, width=width, height=height)
        if on_change:
            self.__var.trace_add("write", lambda *args: on_change()) # type: ignore
        self.__on_change = on_change
        self.__text = text
        self.__width = self.__entry.winfo_reqwidth()
        self.__height = height
        self.__x = x
        self.__y = y

    @property
    def text(self):
        return self.__var.get()
    @text.setter
    def text(self, value):
        self.__var.set(value)
        self.__text = value

    @property
    def width(self):
        return self.__width
    @width.setter
    def width(self, value):
        self.__width = value
        self.__entry.place_configure(width=value)

    @property
    def height(self):
        return self.__height
    @height.setter
    def height(self, value):
        self.__height = value
        self.__entry.place_configure(height=value)

    @property
    def x(self):
        return self.__x
    @x.setter
    def x(self, value):
        self.__x = value
        self.__entry.place_configure(x=value)

    @property
    def y(self):
        return self.__y
    @y.setter
    def y(self, value):
        self.__y = value
        self.__entry.place_configure(y=value)

    def remove(self):
        self.__entry.destroy()

class CheckboxWidget:
    def __init__(self, root, on_click: Callable, text: str, width: int, height: int, x: int, y: int):
        self.__var = tk.BooleanVar()
        self.__cb = tk.Checkbutton(root, text=text, variable=self.__var, command=on_click)
        self.__cb.place(x=x, y=y, width=width, height=height)
        self.__on_click = on_click
        self.__text = text
        self.__width = self.__cb.winfo_reqwidth()
        self.__height = height
        self.__x = x
        self.__y = y

    @property
    def text(self):
        return self.__cb['text']
    @text.setter
    def text(self, value):
        self.__cb['text'] = value
        self.__text = value

    @property
    def width(self):
        return self.__width
    @width.setter
    def width(self, value):
        self.__width = value
        self.__cb.place_configure(width=value)

    @property
    def height(self):
        return self.__height
    @height.setter
    def height(self, value):
        self.__height = value
        self.__cb.place_configure(height=value)

    @property
    def x(self):
        return self.__x
    @x.setter
    def x(self, value):
        self.__x = value
        self.__cb.place_configure(x=value)

    @property
    def y(self):
        return self.__y
    @y.setter
    def y(self, value):
        self.__y = value
        self.__cb.place_configure(y=value)

    def remove(self):
        self.__cb.destroy()


class Screen:
    def __init__(self, title:str ="", width: int=320, height: int=240, x: int=None, y: int=None):
        self.__root = tk.Tk()
        self.__root.transient()
        self.__root.grab_set()
        self.__root.withdraw()  # Start hidden
        self.__root.title(title)
        self.__root.resizable(False, False)
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
        self.__root.attributes('-toolwindow', True) 
        self.__root.attributes('-topmost', True)
        self.__widgets = []

        # Center window if x/y not provided
        screen_w = self.__root.winfo_screenwidth()
        screen_h = self.__root.winfo_screenheight()
        if x is None:
            x = (screen_w - width) // 2
        if y is None:
            y = (screen_h - height) // 2
        self.__root.geometry(f"{width}x{height}+{x}+{y}")

        self.__root.bind("<Escape>", lambda e: self.close())

        self.__title = title
        self.__width = width
        self.__height = height
        self.__x = x
        self.__y = y

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        self.__title = value
        self.__root.title(value)

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.__width = value
        self.__root.geometry(f"{self.__width}x{self.__height}+{self.__x}+{self.__y}")

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        self.__height = value
        self.__root.geometry(f"{self.__width}x{self.__height}+{self.__x}+{self.__y}")

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value
        self.__root.geometry(f"{self.__width}x{self.__height}+{self.__x}+{self.__y}")

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value
        self.__root.geometry(f"{self.__width}x{self.__height}+{self.__x}+{self.__y}")

    def show(self):
        self.__root.deiconify()
        self.__root.lift()
        #self.__root.mainloop()
        self.__root.wait_window()

    def close(self):
        self.__root.quit()
        self.__root.destroy()

    def add_button(self, on_click: Callable=None, text: str="", width: int=None, height: int=20, x: int=0, y: int=0, down=None, right=None) -> ButtonWidget:
        if down:
            x = down.x
            y = down.y + down.height + 10
        if right:
            y = right.y
            x = right.x + right.width + 10
        btn = ButtonWidget(self.__root, on_click, text, width, height, x, y)
        self.__widgets.append(btn)
        return btn

    def text_input(self, on_change: Callable=None, text: str="", width: int=None, height: int=20, x: int=0, y: int=0, down=None, right=None) -> TextInputWidget:
        if down:
            x = down.x
            y = down.y + down.height + 10
        if right:
            y = right.y
            x = right.x + right.width + 10
        txt = TextInputWidget(self.__root, on_change, text, width, height, x, y)
        self.__widgets.append(txt)
        return txt

    def add_checkbox(self, on_click: Callable=None, text: str="", width: int=None, height: int=20, x: int=0, y: int=0, down=None, right=None) -> CheckboxWidget:
        if down:
            x = down.x
            y = down.y + down.height + 10
        if right:
            y = right.y
            x = right.x + right.width + 10
        cb = CheckboxWidget(self.__root, on_click, text, width, height, x, y)
        self.__widgets.append(cb)
        return cb
    
    def input_dialog(self, title: str="", prompt: str="") -> str | None:
        self.__root.attributes('-topmost', False)
        result = simpledialog.askstring(title, prompt)
        self.__root.attributes('-topmost', True)
        return result
