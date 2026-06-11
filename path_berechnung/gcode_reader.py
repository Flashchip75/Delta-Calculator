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

            j_data = self._smooth_corners(j_data, blend_dist=0.05)

        return j_data

    def _smooth_corners(self, j_data, blend_dist=0.005):
        """
        Replaces sharp corners between consecutive lines with tangent arcs.
        Safely ignores Arcs, Beziers, or any other segments without 'pts'.
        """
        if len(j_data) < 2:
            return j_data

        new_data = []
        
        def safe_copy(item):
            new_item = dict(item)
            if "pts" in new_item:
                new_item["pts"] = [list(pt) for pt in new_item["pts"]]
            return new_item

        current_segment = safe_copy(j_data[0])
        
        for i in range(len(j_data) - 1):
            L1 = current_segment
            L2 = safe_copy(j_data[i+1])
            
            if L1.get("type") != "Line" or L2.get("type") != "Line" or "pts" not in L1 or "pts" not in L2:
                new_data.append(L1)
                current_segment = L2
                continue
                
            p0 = np.array(L1["pts"][0])
            p1 = np.array(L1["pts"][1]) # The shared corner
            p2 = np.array(L2["pts"][1])
            
            d1 = p1 - p0  # Direction of first line
            d2 = p2 - p1  # Direction of second line
            
            len1 = np.linalg.norm(d1)
            len2 = np.linalg.norm(d2)
            
            if len1 < 1e-6 or len2 < 1e-6:
                new_data.append(L1)
                current_segment = L2
                continue
                
            d1_u = d1 / len1
            d2_u = d2 / len2
            
            # Calculate the turning normal
            cross_prod = np.cross(d1_u, d2_u)
            cross_len = np.linalg.norm(cross_prod)
            
            if cross_len < 1e-5: # Lines are straight
                new_data.append(L1)
                current_segment = L2
                continue
                
            n = cross_prod / cross_len
            
            d = min(blend_dist, len1 * 0.45, len2 * 0.45)
            
            # Cut back from the corner
            A = p1 - d1_u * d  
            B = p1 + d2_u * d  
            
            L1["pts"][1] = A.tolist()
            L2["pts"][0] = B.tolist()
            
            # Angle of the turn
            dot_val = np.clip(np.dot(d1_u, d2_u), -1.0, 1.0)
            theta = np.arccos(dot_val)
            
            # Radius
            r = d * np.tan((np.pi - theta) / 2.0)
            
            # Inward normal vector (points from line 1 towards the center of the arc)
            n_in1 = np.cross(n, d1_u)
            
            # Center of arc
            c = A + n_in1 * r
            
            # Arc axes: u points to start (A), v aligns with the starting tangent (d1_u)
            u = (A - c) / r
            v = d1_u 
            
            # The sweep angle is exactly the turning angle
            start_angle = 0.0
            end_angle = float(theta)
            
            arc = {
                "type": "Arc",
                "c": c.tolist(),
                "r": float(r),
                "u": u.tolist(),
                "v": v.tolist(),
                "a": [start_angle, end_angle]
            }
            
            new_data.append(L1)
            new_data.append(arc)
            
            current_segment = L2
            
        new_data.append(current_segment)
        return new_data