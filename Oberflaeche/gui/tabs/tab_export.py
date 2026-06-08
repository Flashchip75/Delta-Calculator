from tkinter import ttk
from Oberflaeche.gui.tabs.tab_base import BaseTab
from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *


class ExportTab(BaseTab):

    def build_left(self):
        ttk.Label(self, text="Export").pack(anchor="w")

        calc_button = ttk.Button(self, text="Calc All")
        calc_button.pack(fill="x")
        #TODO: Nur Calc kin neu?
        #TODO: Wie Pfad in csv_line eingeben

        csv_line = TextLine(self, "Program File")
        csv_line.pack(fill="x")
        #TODO: Anzeigen von Pfad, Rückspeichern von Pfad für Steuerung, Validierung

        serial_line = TextLine(self, "Serial Connection")
        serial_line.pack(fill="x")
        #TODO: Button zum Prüfen der Serial
        # Wann wird serial eröffnet?
        # Wie status Prüfen

        run_button = ttk.Button(self, text="RUN")
        run_button.pack(fill="x")
        # TODO: Threading Etablieren