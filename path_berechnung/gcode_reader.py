import numpy as np
from gcodeparser import GcodeParser

def read_gcode(filepath) -> list:
    return gcode_reader(filepath).gcode_to_profile()

class gcode_reader:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._unit_scale: float = 0.001  # default: mm -> m

    def gcode_to_profile(self) -> list:
        with open(self.filepath) as f:
            parser = GcodeParser(f.read())

        pos = {"X": 0.0, "Y": 0.0, "Z": 0.0}
        j_data = []

        for l in parser.lines:
            # Track unit mode as it changes throughout the file
            if l.command == ("G", 21):
                self._unit_scale = 0.001   # mm -> m
                print("G21: Units set to mm")
                continue
            if l.command == ("G", 20):
                self._unit_scale = 0.0254  # inch -> m
                print("G20: Units set to inch")
                continue

            if l.command not in {("G", 0), ("G", 1)}:
                continue

            prev = pos.copy()

            for a in ("X", "Y", "Z"):
                if a in l.params:
                    pos[a] = float(l.params[a])*self._unit_scale

            if prev != pos:
                j_data.append({
                    "type": "Line",
                    "pts": [
                        [prev["X"], prev["Y"], prev["Z"]],
                        [pos["X"], pos["Y"], pos["Z"]],
                    ]
                })

        return j_data