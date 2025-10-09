"""
    @author RazrCraft (Modified by x_xmalo)
    @create date 2025-07-05 07:58:44
    @modify date 2025-10-09 01:25:00
    @desc A helper library for creating simple screens with Tkinter
"""
# pylint: disable=W0238
import tkinter as tk
from tkinter import simpledialog
from typing import Callable, Optional

##############################################################################
# Additional Options Helper
##############################################################################

def add_options(widget, **options):
    if not options:
        return
    valid = set(widget.keys())
    clean = {k: v for k, v in options.items() if k in valid}
    if clean:
        widget.config(**clean)

##############################################################################
# Base Widget Properties
##############################################################################  

class Base:
    def __init__(self, widget: tk.Widget, *, width: int, height: int, x: int, y: int, **options):
        self._w = widget
        self._width = width if width is not None else widget.winfo_reqwidth()
        self._height = height
        self._x = x
        self._y = y
        self.place()
        add_options(self._w, **options)

    def place(self):
        self._w.place(x=self._x, y=self._y, width=self._width, height=self._height)

    @property
    def width(self): return self._width
    @width.setter
    def width(self, v): self._width = v; self.place()

    @property
    def height(self): return self._height
    @height.setter
    def height(self, v): self._height = v; self.place()

    @property
    def x(self): return self._x
    @x.setter
    def x(self, v): self._x = v; self.place()

    @property
    def y(self): return self._y
    @y.setter
    def y(self, v): self._y = v; self.place()

    def style(self, **options): add_options(self._w, **options)
    def remove(self): self._w.destroy()

##############################################################################
# Label
##############################################################################

class LabelWidget(Base):
    def __init__(self, root, text: str, width: int, height: int, x: int, y: int, **options):
        super().__init__(tk.Label(root, text=text, width=width or 0), width=width, height=height, x=x, y=y, **options)

    @property
    def text(self): return self._w['text']
    @text.setter
    def text(self, v): self._w['text'] = v
        
##############################################################################
# Button
##############################################################################

class ButtonWidget(Base):
    def __init__(self, root, on_click: Optional[Callable], text: str, width: int, height: int, x: int, y: int, **options):
        super().__init__(tk.Button(root, text=text, height=1, command=on_click), width=width, height=height, x=x, y=y, **options)

    @property
    def text(self): return self._w['text']
    @text.setter
    def text(self, v): self._w['text'] = v

##############################################################################
# Text Input (Entry)
##############################################################################

class TextInputWidget(Base):
    def __init__(self, root, on_change: Optional[Callable], text: str, width: int, height: int, x: int, y: int, **options):
        self._var = tk.StringVar(value=text)
        entry = tk.Entry(root, textvariable=self._var, width=width or 0)
        super().__init__(entry, width=width, height=height, x=x, y=y, **options)
        if on_change: self._var.trace_add("write", lambda *args: on_change())

    @property
    def text(self): return self._var.get()
    @text.setter
    def text(self, v): self._var.set(v)

##############################################################################
# Checkbox
##############################################################################

class CheckboxWidget(Base):
    def __init__(self, root, on_click: Optional[Callable], text: str, width: int, height: int, x: int, y: int, **options):
        self._var = tk.BooleanVar()
        cb = tk.Checkbutton(root, text=text, variable=self._var, command=on_click)
        super().__init__(cb, width=width, height=height, x=x, y=y, **options)

    @property
    def text(self): return self._w['text']
    @text.setter
    def text(self, v): self._w['text'] = v

##############################################################################
# Screen
##############################################################################

class Screen:
    def __init__(self, title: str = "", width: int = 320, height: int = 240, x: int = None, y: int = None, **options):
        self._root = tk.Tk()
        self._root.transient(); self._root.grab_set(); self._root.withdraw()
        self._root.title(title); self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", self.close)
        self._root.attributes('-toolwindow', True); self._root.attributes('-topmost', True)

        sw, sh = self._root.winfo_screenwidth(), self._root.winfo_screenheight()
        x = (sw - width)//2 if x is None else x
        y = (sh - height)//2 if y is None else y
        self._width, self._height, self._x, self._y = width, height, x, y
        self.apply_geometry()
        self._root.bind("<Escape>", lambda e: self.close())
        add_options(self._root, **options)
        self._widgets = []

    def apply_geometry(self):
        self._root.geometry(f"{self._width}x{self._height}+{self._x}+{self._y}")

    @property
    def width(self): return self._width
    @width.setter
    def width(self, v): self._width = v; self.apply_geometry()
    @property
    def height(self): return self._height
    @height.setter
    def height(self, v): self._height = v; self.apply_geometry()
    @property
    def x(self): return self._x
    @x.setter
    def x(self, v): self._x = v; self.apply_geometry()
    @property
    def y(self): return self._y
    @y.setter
    def y(self, v): self._y = v; self.apply_geometry()
    @property
    def title(self): return self._root.title()
    @title.setter
    def title(self, v): self._root.title(v)

    def show(self): self._root.deiconify(); self._root.lift(); self._root.wait_window()
    def close(self): self._root.quit(); self._root.destroy()

    def flow(self, width, height, x, y, down, right):
        if down:  x, y = down.x, down.y + down.height + 10
        if right: x, y = right.x + right.width + 10, right.y
        return width, height, x, y

##############################################################################
# Widget Creation Methods
##############################################################################

    def add_label(self, text="", width=None, height=20, x=0, y=0, down=None, right=None, **options):
        width, height, x, y = self.flow(width, height, x, y, down, right)
        w = LabelWidget(self._root, text, width, height, x, y, **options)
        self._widgets.append(w); return w

    def add_button(self, on_click=None, text="", width=None, height=20, x=0, y=0, down=None, right=None, **options):
        width, height, x, y = self.flow(width, height, x, y, down, right)
        w = ButtonWidget(self._root, on_click, text, width, height, x, y, **options)
        self._widgets.append(w); return w

    def text_input(self, on_change=None, text="", width=None, height=20, x=0, y=0, down=None, right=None, **options):
        width, height, x, y = self.flow(width, height, x, y, down, right)
        w = TextInputWidget(self._root, on_change, text, width, height, x, y, **options)
        self._widgets.append(w); return w

    def add_checkbox(self, on_click=None, text="", width=None, height=20, x=0, y=0, down=None, right=None, **options):
        width, height, x, y = self.flow(width, height, x, y, down, right)
        w = CheckboxWidget(self._root, on_click, text, width, height, x, y, **options)
        self._widgets.append(w); return w

    def input_dialog(self, title: str = "", prompt: str = "") -> str | None:
        self._root.attributes('-topmost', False)
        try:
            return simpledialog.askstring(title, prompt)
        finally:
            self._root.attributes('-topmost', True)
