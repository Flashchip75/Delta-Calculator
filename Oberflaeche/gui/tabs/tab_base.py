import tkinter as tk
from tkinter import ttk

# Baut einen Grundlagen tab auf den verschiedene Elemente gebased werden können
class BaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.columnconfigure(0, weight=0)   # links
        self.columnconfigure(1, weight=1)   # rechts
        self.rowconfigure(0, weight=1)

        self.left_frame = ttk.Frame(self, padding=10)
        self.left_frame.grid(row=0, column=0, sticky="nsw")

        self.right_frame = ttk.Frame(self, padding=10)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.build_left()
        self.build_right()

    def build_left(self): # Platzhaltermethode
        pass

    def build_right(self): # Platzhaltermethode
        pass