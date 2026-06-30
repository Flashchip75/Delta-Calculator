import tkinter as tk
from Oberflaeche.help_functions.help_functions import hsv_to_hex, hue_from_string

class TimelineButton(tk.Button):
    """
    TK Button that can take a function with integer parameter.

    Automatically colors itself based on the text assigned to it.
    """
    def __init__(self, master=None, text = "", index: int = 0, command = lambda i: None):
        super().__init__(
            master,
            text=text,
            command=self._internal_command,
        )
        self.index = index
        self.hue = hue_from_string(text)

        # Set onChange Function
        if callable(command):
            self.onPressed = command
        else:
            self.onPressed = lambda i: None

        self.normal_color()

    def _internal_command(self):
        self.onPressed(self.index)

    def highlight_color(self):
        self.configure(
            foreground=hsv_to_hex(self.hue, 1, 0),
            background=hsv_to_hex(self.hue, 0.5, 0.9),
            font=("kDefaultFont", 8, "bold")
        )

    def normal_color(self):
        self.configure(
            foreground=hsv_to_hex(self.hue, 1, 0.25),
            background=hsv_to_hex(self.hue, 0.25, 0.75),
            font=("kDefaultFont", 8)
        )