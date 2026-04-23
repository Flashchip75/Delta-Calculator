from gcodeparser import GcodeParser

def extract_xyz(filepath: str) -> list[dict]:
    """
    Parse a G-code file and return a list of XYZ positions
    for all G0/G1 move commands. Carries forward the last
    known position when an axis isn't specified.
    """
    with open(filepath, "r") as f:
        gcode = f.read()

    parser = GcodeParser(gcode, include_comments=True)

    pos = {"X": 0.0, "Y": 0.0, "Z": 0.0}
    positions = []

    MOVE_COMMANDS = {("G", 0), ("G", 1)}  # rapid + linear move

    for line in parser.lines:
        if line.command not in MOVE_COMMANDS:
            continue

        # Update only the axes present on this line
        for axis in ("X", "Y", "Z"):
            if axis in line.params:
                pos[axis] = float(line.params[axis])

        positions.append(dict(pos))  # snapshot of current position

    return positions


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "test.gcode"
    pts = extract_xyz(path)

    print(f"Found {len(pts)} move positions\n")
    for i, p in enumerate(pts[:20]):  # print first 20
        print(f"  [{i:4d}]  X={p['X']:8.3f}  Y={p['Y']:8.3f}  Z={p['Z']:8.3f}")

    if len(pts) > 20:
        print(f"  ... and {len(pts) - 20} more")