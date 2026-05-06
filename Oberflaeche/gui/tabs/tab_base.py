from tkinter import ttk

class BaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.left_frame = ttk.Frame(self, padding=10)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        self.build_left()

    def build_left(self):
        pass