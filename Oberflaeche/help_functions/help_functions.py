# Funktionen die nicht zum erstellen von widgets dienen bspw. schreiben in .json, Fehlermendungen

import math
import colorsys

def hsv_to_hex(h, s, v):
    r, g, b = [math.floor(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    return f'#{r:02x}{g:02x}{b:02x}'
