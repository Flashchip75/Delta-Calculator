; Simple test gcode - square with Z step
G21        ; units: mm
G90        ; absolute positioning

; Move to start, clear Z
G0 Z5.0
G0 X0.0 Y0.0

; Plunge
G1 Z0.0 F200

; Draw a 50x50mm square
G1 X50.0 Y0.0  F1000
G1 X50.0 Y50.0
G1 X0.0  Y50.0
G1 X0.0  Y0.0

; Step up and do a smaller square at Z=2
G0 Z2.0
G1 X25.0 Y10.0 F1000
G1 X40.0 Y10.0
G1 X40.0 Y40.0
G1 X10.0 Y40.0
G1 X10.0 Y10.0

; Retract and go home
G0 Z10.0
G0 X0.0 Y0.0