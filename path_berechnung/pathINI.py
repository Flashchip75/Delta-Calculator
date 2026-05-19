init_config = {
# -----------------------------------------------------
# Units
# -----------------------------------------------------
"units": {
    "position": "mm",
    "time": "s",
    "angle": "deg"
},


# -----------------------------------------------------
# Geometrien
# -----------------------------------------------------
"geometries": {

    "line": {
        "parameters": {
            "start": "Vector3D",
            "end": "Vector3D",
            "duration": "float"
        }
    },

    "bezier": {
        "parameters": {
            "control_points": "List[Vector3D, length=4]",
            "duration": "float"
        }
    },

    "arc": {
        "parameters": {
            "center": "Vector3D",
            "radius": "float",
            "plane": ["xy", "xz", "yz"],
            "start_angle": "float",
            "end_angle": "float",
            "duration": "float"
        }
    }

},


# -----------------------------------------------------
# Zeitgesetz (pro Kurve)
# -----------------------------------------------------
"time_law": {
    "type": "List[Tuple[int, int, float]]"
}
}
