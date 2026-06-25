from Oberflaeche.gui.designelemente.custom_widgets.property_lines import *


class initial_condition_frame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.position = NumberLine(
            self,
            "Start Position",
            3,
            uc.UnitLength(),
            defaults=(0.0, 0.0, 0.0),
            defaultUnit="mm",
            colored=True,
        )
        self.position.pack(fill=tk.X)

        self.velocity = NumberLine(
            self,
            "Start Velocity",
            1,
            uc.UnitVelocity(),
            defaults=(0.0, 0.0, 0.0),
            defaultUnit="m/s",
            colored=False,
        )
        self.velocity.pack(fill=tk.X)
        self.velocity.inputs[0].state(["disabled"])
        self.velocity.unitSelector.state(["disabled"])