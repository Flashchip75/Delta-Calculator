import numpy as np
from gcodeparser import GcodeParser

def read_gcode(filepath):
    j_data = gcode_reader(filepath).gcode_to_profile()
    return j_data

class gcode_reader:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def gcode_to_profile(self) -> list:
        with open(self.filepath) as f:
            parser = GcodeParser(f.read())

        pos = {"X": 0.0, "Y": 0.0, "Z": 0.0}
        j_data = []

        for l in parser.lines:
            if l.command not in {("G", 0), ("G", 1)}:
                continue

            prev = pos.copy()

            for a in ("X", "Y", "Z"):
                if a in l.params:
                    pos[a] = float(l.params[a])
                    pos[a] = pos[a]*0.01  # mm -> m

            if prev != pos:
                j_data.append({
                    "type": "Line",
                    "pts": [
                        [prev["X"], prev["Y"], prev["Z"]],
                        [pos["X"], pos["Y"], pos["Z"]],
                    ]
                })

        return j_data