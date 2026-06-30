from Oberflaeche.gui.designelemente.custom_widgets.input_widgets import *
from Oberflaeche.help_functions import help_functions as util


# Line Widgets

class PropertyLine(tk.Frame):
    """
    Masterclass for all property lines used for the left-side input fields.

    This implements:
        - line label (on column 0)
        - grid columns 1 and 2 for additional widgets
        - get() method to get and package properties from this line
        - updateLine() method to run the two callbacks below in order
        - writeProperties(value) callback to write and store the get() properties somewhere outside of this object
        - onLineChanged() callback to signal new values

    Subclasses must do the following:
        - override get() to retrieve and process their specific properties
        - bind the updateLine() method to all onValueChanged() callbacks from their input widgets
    """
    def __init__(self, master=None, labelText: str = "", *, writePropertiesFunction=None, onLineChangedFunction=None,
                 **kwargs):
        super().__init__(
            master,
            bg="#ffffff",
            name="lineFrame(" + labelText.replace(" ", "_") + ")",
            **kwargs
        )
        # Configure 3 Rows
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)  # Left: Text Label, adjustable
        self.columnconfigure(1, weight=0)  # Center: Input Fields, fixed
        self.columnconfigure(2, weight=0)  # Right: Input Fields or Units, fixed

        # Initialize Line Label
        self.label = ttk.Label(
            self,
            width=1,
            text=labelText,
            background="#ffffff",
            foreground="#000000",
            name="lineMainLabel(" + labelText.replace(" ", "_") + ")"
        )
        self.label.configure()
        self.label.grid(row=0, column=0, sticky="nsew")

        # Set onChange Function
        if callable(onLineChangedFunction):
            self.onLineChanged = onLineChangedFunction
        else:
            self.onLineChanged = lambda: None

        # Set writeProperties Function
        if callable(writePropertiesFunction):
            self.writeProperties = writePropertiesFunction
        else:
            self.writeProperties = lambda _: None

    def get(self):
        return None

    def updateLine(self, writeOnly: bool = False):
        self.writeProperties(self.get())
        if not writeOnly:
            self.onLineChanged()


class NumberLine(PropertyLine):
    """
    PropertyLine used for inputting numerical values and vectors (tuples), optionally with SI unit conversion.
    """
    def __init__(self, master=None, labelText: str = "", inputCount: int = 1, units: dataclass = uc.Unitless(), *,
                 defaults: tuple = None, defaultUnit: str = "", writePropertiesFunction=None, onLineChangedFunction=None,
                 colored: bool = False, colorShift: float = 0.0, **kwargs):
        super().__init__(
            master,
            labelText,
            onLineChangedFunction=onLineChangedFunction,
            writePropertiesFunction=writePropertiesFunction,
            **kwargs
        )
        # Initialize Frame as Container for the Input Fields
        # (Needed for filling a given width with multiple fields)
        self.inputContainer = tk.Frame(
            self,
            bg="#ffffff",
            width=150,
            name="lineInputFrame(" + labelText.replace(" ", "_") + ")"
        )
        self.inputContainer.grid(row=0, column=1, sticky="nsew")
        self.inputContainer.grid_propagate(False)  # Enforce fixed Width

        # Initialize Entry Widget List
        self.inputs = []

        # Check external Defaults
        defaults = defaults if defaults else ("0.0",) * inputCount

        # Initialize new Columns and Entries per Input
        for i in range(inputCount):
            self.inputContainer.columnconfigure(i, weight=1)

            # Text Color in the Field
            # (Either all black or evenly spaced around the color wheel)
            widgetColor = util.hsv_to_hex(i / inputCount + colorShift, 1, 0.75) if colored else "#000000"

            inputWidget = FloatEntry(
                self.inputContainer,
                defaults[i],
                onValueChangedFunction=self.updateLine,
                width=1,
                foreground=widgetColor,
                name="lineFloatEntry" + str(i) + "(" + labelText.replace(" ", "_") + ")"
            )
            inputWidget.grid(row=0, column=i, sticky="nsew")
            self.inputs.append(inputWidget)

        # Initialize Unit Selector Combobox
        self.unitSelector = UnitSelectorCombobox(
            self,
            units,
            defaultUnit=defaultUnit,
            onValueChangedFunction=self.updateLine,
            name="lineUnitSelector(" + labelText.replace(" ", "_") + ")"
        )
        self.unitSelector.grid(row=0, column=2, sticky="nsew")

    def get(self):
        unitFactor = self.unitSelector.get()[1]
        return tuple([widget.get() * unitFactor for widget in self.inputs])


class IncrementorLine(PropertyLine):
    """
    PropertyLine used for inputting integer values, optionally with SI unit conversion.
    """
    def __init__(self, master=None, labelText: str = "", units: dataclass = uc.Unitless(), *,
                 default: int = 0, defaultUnit: str = "", writePropertiesFunction=None, onLineChangedFunction=None, **kwargs):
        super().__init__(
            master,
            labelText,
            onLineChangedFunction=onLineChangedFunction,
            writePropertiesFunction=writePropertiesFunction,
            **kwargs
        )
        # Initialize Frame as Container for the Input Fields
        # (Needed for filling a given width with multiple fields)
        self.inputContainer = tk.Frame(
            self,
            bg="#ffffff",
            width=150,
            name="lineInputFrame(" + labelText.replace(" ", "_") + ")"
        )
        self.inputContainer.grid(row=0, column=1, sticky="nsew")
        self.inputContainer.rowconfigure(0, weight=1)
        self.inputContainer.columnconfigure(0, weight=1)
        self.inputContainer.grid_propagate(False) # Enforce fixed Width

        # Initialize IntSpinbox as Input
        self.input = IntSpinbox(
                self.inputContainer,
                default,
                onValueChangedFunction=self.updateLine,
                width=1,
                foreground="#000000",
                name="lineIntSpinbox(" + labelText.replace(" ", "_") + ")"
            )
        self.input.grid(row=0, column=0, sticky="nsew")

        # Initialize Unit Selector Combobox
        self.unitSelector = UnitSelectorCombobox(
            self,
            units,
            defaultUnit=defaultUnit,
            onValueChangedFunction=self.updateLine,
            name="lineUnitSelector(" + labelText.replace(" ", "_") + ")"
        )
        self.unitSelector.grid(row=0, column=2, sticky="nsew")

        self.returnAsInteger = isinstance(units,uc.Unitless)

    def get(self):
        unitFactor = self.unitSelector.get()[1]
        if self.returnAsInteger:
            return int(self.input.get() * unitFactor)
        else:
            return self.input.get() * unitFactor


class CheckboxLine(PropertyLine):
    """
    PropertyLine used for inputting a boolean value via a combobox.
    """
    def __init__(self, master=None, labelText: str = "", *,
                 default: bool = False, checkboxText: str = "", writePropertiesFunction=None, onLineChangedFunction=None, **kwargs):
        super().__init__(
            master,
            labelText,
            onLineChangedFunction=onLineChangedFunction,
            writePropertiesFunction=writePropertiesFunction,
            **kwargs
        )
        # Initialize IntVar to store the state of the Checkbutton
        # (Checkbutton does not have a get() of it's own)
        self.state = tk.IntVar()

        # Initialize Checkbutton
        self.input = tk.Checkbutton(
            self,
            bg="#ffffff",
            width=27,
            name="lineCheckbox(" + labelText.replace(" ", "_") + ")",
            variable=self.state,
            text=checkboxText,
            command=self.updateLine
        )
        self.input.grid(row=0, column=1, columnspan=2, sticky="nsew")

        # Set default state
        if default:
            self.input.select()
        else:
            self.input.deselect()

    def get(self):
        return bool(self.state.get())


class TextLine(PropertyLine):
    """
    PropertyLine used for inputting string values in a text field.
    """
    def __init__(self, master=None, labelText: str = "", *,
                 default: str = "", writePropertiesFunction=None, onLineChangedFunction=None,
                 colored: bool = False, colorShift: float = 0.0, **kwargs):
        super().__init__(
            master,
            labelText,
            onLineChangedFunction=onLineChangedFunction,
            writePropertiesFunction=writePropertiesFunction,
            **kwargs
        )
        # Initialize Frame as Container for the Input Fields
        # (Needed for filling a given width with multiple fields)
        self.inputContainer = tk.Frame(
            self,
            bg="#ffffff",
            width=221,
            name="lineInputFrame(" + labelText.replace(" ", "_") + ")"
        )
        self.inputContainer.grid(row=0, column=1, columnspan=2, sticky="nsew")
        self.inputContainer.grid_propagate(False)  # Enforce fixed Width

        self.inputContainer.columnconfigure(0, weight=1)

        # Text Color in the Field
        # (Either all black or evenly spaced around the color wheel)
        widgetColor = util.hsv_to_hex(colorShift, 1, 0.75) if colored else "#000000"

        # Initialize Entry Widget List
        self.input = GenericEntry(
            self.inputContainer,
            default,
            onValueChangedFunction=self.updateLine,
            width=1,
            foreground=widgetColor,
            name="lineGenericEntry(" + labelText.replace(" ", "_") + ")"
        )
        self.input.grid(row=0, column=0, sticky="nsew")

    def get(self):
        return self.input.get()


class DropdownLine(PropertyLine):
    """
    PropertyLine used for selecting an item from the options in a list or dict.
    """
    def __init__(self, master=None, labelText: str = "", options: list | dict = [""], *,
                 defaultIndex: int = 0, writePropertiesFunction=None, onLineChangedFunction=None,
                 colored: bool = False, colorShift: float = 0.0, **kwargs):
        super().__init__(
            master,
            labelText,
            onLineChangedFunction=onLineChangedFunction,
            writePropertiesFunction=writePropertiesFunction,
            **kwargs
        )
        # Initialize Frame as Container for the Input Fields
        # (Needed for filling a given width with multiple fields)
        self.inputContainer = tk.Frame(
            self,
            bg="#ffffff",
            width=221,
            name="lineInputFrame(" + labelText.replace(" ", "_") + ")"
        )
        self.inputContainer.grid(row=0, column=1, columnspan=2, sticky="nsew")
        self.inputContainer.grid_propagate(False)  # Enforce fixed Width

        self.inputContainer.columnconfigure(0, weight=1)

        # Text Color in the Field
        # (Either all black or evenly spaced around the color wheel)
        widgetColor = util.hsv_to_hex(colorShift, 1, 0.75) if colored else "#000000"

        # Initialize Entry Widget List
        self.input = ListCombobox(
            self.inputContainer,
            options,
            defaultIndex,
            onValueChangedFunction=self.updateLine,
            width=1,
            foreground=widgetColor,
            name="lineListCombobox(" + labelText.replace(" ", "_") + ")"
        )
        self.input.grid(row=0, column=0, sticky="nsew")

    def get(self):
        return self.input.get()