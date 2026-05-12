import tkinter as tk
from tkinter import messagebox, ttk

from Oberflaeche.help_functions.struct_geo_data import GeoData, MotorGeoData


class GeoInput(ttk.Frame):
    def __init__(self, parent, geo_data: GeoData):
        super().__init__(parent)

        self.geo_data = geo_data
        self.current_mode = geo_data.advanced
        self.advanced_var = tk.BooleanVar(value=geo_data.advanced)
        self.vars: dict[tuple, tk.StringVar] = {}

        ttk.Style().configure("SectionTitle.TLabel", font=("TkDefaultFont", 12, "bold"))

        ttk.Checkbutton(
            self,
            text="advanced",
            variable=self.advanced_var,
            command=self._toggle_mode,
        ).pack(anchor="w")

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.body = ttk.Frame(self.canvas)
        self.window_id = self.canvas.create_window((0, 0), window=self.body, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body.bind("<Configure>", self._resize_scroll_region)
        self.canvas.bind("<Configure>", self._resize_body)

        self._render()

    def _render(self):
        self.vars.clear()

        for child in self.body.winfo_children():
            child.destroy()

        if self.current_mode:
            self._section("Global", [
                ("gravity", ("global", "gravity"), 3, "m/s^2"),
                ("mass", ("global", "mass_kg"), 1, "kg"),
                ("payload mass", ("global", "payload_mass"), 1, "kg"),
                ("singularity margin", ("global", "singularity_margin_deg"), 1, "deg"),
            ])
            self._section("Workspace", [
                ("resolution", ("workspace", "resolution"), 1, ""),
                ("range_x", ("workspace", "range_x"), 2, "m"),
                ("range_y", ("workspace", "range_y"), 2, "m"),
                ("range_z", ("workspace", "range_z"), 2, "m"),
            ])

            for name, motor in self.geo_data.motors.items():
                self._motor_section(name, motor, advanced=True)
        else:
            self._section("Global", [
                ("mass", ("global", "mass_kg"), 1, "kg"),
                ("payload mass", ("global", "payload_mass"), 1, "kg"),
            ])
            self._section("Motoren gemeinsam", [
                ("upper length", ("common", "upper_length"), 1, "m"),
                ("upper mass", ("common", "upper_mass"), 1, "kg"),
                ("lower length", ("common", "lower_length"), 1, "m"),
                ("lower mass", ("common", "lower_mass"), 1, "kg"),
            ])

            for name, motor in self.geo_data.motors.items():
                self._motor_section(name, motor, advanced=False)

        self._update_scrollbar()

    def _section(self, title: str, rows: list[tuple[str, tuple, int, str]]):
        ttk.Label(self.body, text=title, style="SectionTitle.TLabel").pack(
            anchor="w",
            padx=14,
            pady=(12, 4),
        )
        frame = ttk.Frame(self.body, padding=8)
        frame.pack(fill="x", padx=6, pady=(0, 6))
        self._configure_columns(frame)

        for row, (label, key, size, unit) in enumerate(rows):
            self._row(frame, row, label, key, size, unit)

    def _motor_section(self, name: str, motor: MotorGeoData, advanced: bool):
        rows = [("position", ("motor", name, "position"), 3, "m")]

        if advanced:
            rows += [
                ("upper length", ("motor", name, "upper_length"), 1, "m"),
                ("upper mass", ("motor", name, "upper_mass"), 1, "kg"),
                ("lower length", ("motor", name, "lower_length"), 1, "m"),
                ("lower mass", ("motor", name, "lower_mass"), 1, "kg"),
                ("theta min", ("motor", name, "theta_min"), 1, "deg"),
                ("theta max", ("motor", name, "theta_max"), 1, "deg"),
            ]

        self._section(f"Motor {name}", rows)

    def _row(self, parent, row: int, label: str, key: tuple, size: int, unit: str):
        ttk.Label(parent, text=label, width=17).grid(row=row, column=0, sticky="w", pady=5)

        if size == 1:
            entry = ttk.Entry(parent, textvariable=self._var(key))
            entry.grid(row=row, column=1, columnspan=3, sticky="ew", pady=5)
            entry.bind("<Return>", self.apply_inputs)
        else:
            for index in range(size):
                entry = ttk.Entry(parent, textvariable=self._var((*key, index)), width=10)
                entry.grid(row=row, column=index + 1, sticky="ew", padx=(0, 6), pady=5)
                entry.bind("<Return>", self.apply_inputs)

        ttk.Label(parent, text=unit, width=5).grid(row=row, column=4, sticky="w", padx=(2, 0), pady=5)

    def _var(self, key: tuple) -> tk.StringVar:
        if key in self.vars:
            return self.vars[key]

        value = self._value_for(key)
        self.vars[key] = tk.StringVar(value=str(value))
        return self.vars[key]

    def _value_for(self, key: tuple):
        area = key[0]

        if area == "global":
            return getattr(self.geo_data, key[1]) if len(key) == 2 else self.geo_data.gravity[key[2]]
        if area == "workspace":
            return getattr(self.geo_data, f"workspace_{key[1]}") if key[1] == "resolution" else getattr(self.geo_data, key[1])[key[2]]
        if area == "common":
            return getattr(self.geo_data, f"common_{key[1]}")

        motor = self.geo_data.motors[key[1]]
        return getattr(motor, key[2]) if len(key) == 3 else motor.position[key[3]]

    def _configure_columns(self, frame):
        frame.columnconfigure(0, minsize=100)
        for column in range(1, 4):
            frame.columnconfigure(column, weight=1, minsize=58, uniform="inputs")
        frame.columnconfigure(4, minsize=36)

    def apply_inputs(self, _event=None):
        try:
            self._write_visible_values()
            print(self.geo_data)
            return "break" if _event else True
        except ValueError as error:
            messagebox.showerror("Ungueltige Eingabe", str(error), parent=self)
            return "break" if _event else False

    def _write_visible_values(self):
        self.geo_data.advanced = self.current_mode
        self.geo_data.mass_kg = self._number(("global", "mass_kg"))
        self.geo_data.payload_mass = self._number(("global", "payload_mass"))

        if self.current_mode:
            self.geo_data.gravity = self._vector(("global", "gravity"), 3)
            self.geo_data.singularity_margin_deg = self._number(("global", "singularity_margin_deg"))
            self.geo_data.workspace_resolution = int(self._number(("workspace", "resolution")))
            self.geo_data.range_x = self._vector(("workspace", "range_x"), 2)
            self.geo_data.range_y = self._vector(("workspace", "range_y"), 2)
            self.geo_data.range_z = self._vector(("workspace", "range_z"), 2)

        if not self.current_mode:
            self.geo_data.common_upper_length = self._number(("common", "upper_length"))
            self.geo_data.common_upper_mass = self._number(("common", "upper_mass"))
            self.geo_data.common_lower_length = self._number(("common", "lower_length"))
            self.geo_data.common_lower_mass = self._number(("common", "lower_mass"))
            self.geo_data.apply_common_motor_values()

        for name, motor in self.geo_data.motors.items():
            motor.position = self._vector(("motor", name, "position"), 3)

            if self.current_mode:
                motor.upper_length = self._number(("motor", name, "upper_length"))
                motor.upper_mass = self._number(("motor", name, "upper_mass"))
                motor.lower_length = self._number(("motor", name, "lower_length"))
                motor.lower_mass = self._number(("motor", name, "lower_mass"))
                motor.theta_min = self._number(("motor", name, "theta_min"))
                motor.theta_max = self._number(("motor", name, "theta_max"))

    def _toggle_mode(self):
        wanted_mode = self.advanced_var.get()

        if not self.apply_inputs():
            self.advanced_var.set(self.current_mode)
            return

        self.current_mode = wanted_mode
        self.geo_data.advanced = wanted_mode
        self._render()

    def _number(self, key: tuple) -> float:
        raw_value = self.vars[key].get().strip().replace(",", ".")

        try:
            return float(raw_value)
        except ValueError as error:
            raise ValueError(f"'{key[-1]}' muss eine Zahl sein.") from error

    def _vector(self, key: tuple, size: int) -> list[float]:
        return [self._number((*key, index)) for index in range(size)]

    def _resize_scroll_region(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._update_scrollbar()

    def _resize_body(self, event):
        scrollbar_width = self.scrollbar.winfo_reqwidth() if self.scrollbar.winfo_ismapped() else 0
        self.canvas.itemconfigure(self.window_id, width=max(event.width - scrollbar_width, 1))
        self._update_scrollbar()

    def _update_scrollbar(self):
        content_box = self.canvas.bbox("all")

        if not content_box:
            return

        content_height = content_box[3] - content_box[1]
        needs_scrollbar = content_height > self.canvas.winfo_height()

        if needs_scrollbar and not self.scrollbar.winfo_ismapped():
            self.scrollbar.pack(side="right", fill="y")
        elif not needs_scrollbar and self.scrollbar.winfo_ismapped():
            self.scrollbar.pack_forget()
# 4  Funktionalitäten: Advanced, Scrollbar, Eingabefelder, Speicherung in Struct
# classe untergliedern (wo und wie)
#_number direkt über tkinter?
