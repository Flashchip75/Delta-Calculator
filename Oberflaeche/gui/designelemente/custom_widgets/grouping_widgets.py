import tkinter as tk
from tkinter import ttk

class FolderFrame(tk.Frame):
    def __init__(self, master=None, labelText: str="Folder", isOpen: bool = True, isLocked: bool = False, **kwargs):
        super().__init__(
            master,
            **kwargs
        )
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)

        self.button = tk.Button(self, width=2, height=1, command=self.toggle)
        self.button.grid(row=0, column=0, sticky="nsew")

        self.header = tk.Label(self, text=labelText, anchor="w", font=("kDefaultFont", 10, "bold"))
        self.header.grid(row=0, column=1, sticky="nsew")

        self.contentFrame = tk.Frame(self)
        self.contentFrame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.bottomSeperator = ttk.Separator(self, orient="horizontal")
        self.bottomSeperator.grid(row=2, column=0, columnspan=2, sticky="nsew",pady=5)

        self.isOpen = isOpen
        if isOpen:
            self.open()
        else:
            self.close()

        self.isLocked = isLocked
        if isLocked:
            self.lock()
        else:
            self.unlock()

    def open(self):
        self.contentFrame.grid()
        self.contentFrame.grid_propagate(False)
        self.isOpen = True
        self.button.configure(text="\\/")
        self.button.configure(font = ("kDefaultFont", 8, "bold"))

    def close(self):
        self.contentFrame.grid_remove()
        self.isOpen = False
        self.button.configure(text=">")
        self.button.configure(font=("kDefaultFont", 8, "bold"))

    def toggle(self):
        if self.isOpen:
            self.close()
        else:
            self.open()

    def lock(self):
        self.button.configure(state="disabled")
        self.isLocked = True

    def unlock(self):
        self.button.configure(state="normal")
        self.isLocked = False