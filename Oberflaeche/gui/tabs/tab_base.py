from tkinter import ttk

# erzeugt Basisstruktur der Eingabetabs auf der linken Seite. Wird gerufen in tab_....py
class BaseTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.build_left()

    def build_left(self):
        pass