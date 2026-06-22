from sys import maxsize
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from Oberflaeche.help_functions import unit_conversion as uc


# Single Widgets

class FloatEntry(ttk.Entry):
    """
    TTK Entry that can only take values able to be cast to a float.

    The Widget will validate the entered value upon unfocus or when calling get().
    If the value is not a number, it will revert it to the last valid value.
    If the value is a new float, it will keep it and call onValueChanged() afterward.
    """
    def __init__(self, master=None, defaultValue: float | str = 0.0, *, onValueChangedFunction=None, **kwargs):
        # Register Tkinter-Validation
        validateWrapper = (master.register(self._validate), '%P')
        revertWrapper = (master.register(self._revert),)

        super().__init__(
            master,
            validate="focusout",
            validatecommand=validateWrapper,
            invalidcommand=revertWrapper,
            **kwargs  # Additional Keyword Arguments for Entries
        )

        # Set Defaults
        if type(defaultValue) == float:
            self.insert(0, str(defaultValue))
            self.last_valid_value = str(defaultValue)
            self.numerical_value = defaultValue
        else:
            self.insert(0, defaultValue)
            self.last_valid_value = defaultValue
            self.numerical_value = float(defaultValue)

        # Set onChanged Function
        if callable(onValueChangedFunction):
            self.onValueChanged = onValueChangedFunction
        else:
            self.onValueChanged = lambda: None

    def _validate(self, proposed_value: str) -> bool:
        try:
            n = float(proposed_value)  # <- Fails here if value cannot be parsed
        except ValueError:
            return False

        # Only continues here if parsing was successful
        self.last_valid_value = proposed_value
        if not (self.numerical_value == n):
            self.numerical_value = n
            self.onValueChanged()
        return True

    def _revert(self):
        # Reverts to last valid Value
        self.delete(0, tk.END)
        self.insert(0, self.last_valid_value)

    def get(self):
        # Validate on get() in case new input hasn't been validated yet because user is still focussed on this widget
        if self.focus_get() == self:
            if not self._validate(super().get()):
                self._revert()
        return self.numerical_value


class IntSpinbox(ttk.Spinbox):
    """
    TTK Spinbox that can only take values able to be cast to an int.

    The Widget will validate the entered value upon unfocus, spin or when calling get().
    If the value is not an int in the allowed range, it will revert it to the last valid value.
    If the value is a new int, it will keep it and call onValueChanged() afterward.
    """
    def __init__(self, master=None, defaultValue: int | str = 1, *, allowNegative: bool = True, allowZero: bool = True, onValueChangedFunction=None, **kwargs):
        # Register Tkinter-Validation
        validateWrapper = (master.register(self._validate), '%P')
        revertWrapper = (master.register(self._revert),)

        maxValue = maxsize
        if not allowZero and not allowNegative:
            minValue = 1
        elif not allowNegative:
            minValue = 0
        else:
            minValue = -maxValue

        super().__init__(
            master,
            validate="focusout",
            validatecommand=validateWrapper,
            invalidcommand=revertWrapper,
            from_=minValue,
            to=maxValue,
            **kwargs  # Additional Keyword Arguments for Entries
        )

        # Store range flags
        self.allowNegative = allowNegative
        self.allowZero = allowZero

        # Bind Increment and Decrement Actions
        self.bind("<<Increment>>", self._increment)
        self.bind("<<Decrement>>", self._decrement)

        # Set Defaults
        if type(defaultValue) == int:
            self.insert(0, str(defaultValue))
            self.last_valid_value = str(defaultValue)
            self.numerical_value = defaultValue
        elif type(defaultValue) == str:
            self.insert(0, defaultValue)
            self.last_valid_value = defaultValue
            self.numerical_value = int(float(defaultValue))

        # Set onChanged Function
        if callable(onValueChangedFunction):
            self.onValueChanged = onValueChangedFunction
        else:
            self.onValueChanged = lambda: None

    def _increment(self, event):
        self._validate(str(self.numerical_value + 1))

    def _decrement(self, event):
        self._validate(str(self.numerical_value - 1))

    def _validate(self, proposed_value: str) -> bool:
        try:
            nf = float(proposed_value) # <- Fails here if value cannot be parsed
            n  = int(nf)
        except ValueError:
            return False

        if n != nf: return False # String is not a clean representation of an int
        if n == 0 and not self.allowZero: return False # Zero not allowed
        if n < 0 and not self.allowNegative: return False # Negative not allowed

        # Only continues here if parsing was successful
        self.last_valid_value = proposed_value
        if not (self.numerical_value == n):
            self.numerical_value = n
            self.onValueChanged()
        return True

    def _revert(self):
        # Reverts to last valid Value
        self.delete(0, tk.END)
        self.insert(0, self.last_valid_value)

    def get(self):
        # Validate on get() in case new input hasn't been validated yet because user is still focussed on this widget
        if self.focus_get() == self:
            if not self._validate(super().get()):
                self._revert()
        return self.numerical_value


class UnitSelectorCombobox(ttk.Combobox):
    """
    TTK Combobox that can select between different units and provides the conversion factor towards to the corresponding SI unit.

    The Widget will fill the Combobox with all keys from the IUnit dataclass.
    When a selected unit is different from the previous it will call onValueChanged().
    """
    def __init__(self, master=None, units: dataclass = uc.Unitless(), defaultUnit: str = "", *,
                 onValueChangedFunction=None, **kwargs):
        self.units = units
        super().__init__(
            master,
            width=8,
            values=tuple(self.units.getLists()[0]),
            state="readonly"
        )
        defaultUnit = defaultUnit if defaultUnit else self.units.getDefault()
        self.current(self.units.getIndex(defaultUnit))
        self.last_value = self.get()
        self.bind("<<ComboboxSelected>>", self._checkNewSelection)

        # Set onChanged Function
        if callable(onValueChangedFunction):
            self.onValueChanged = onValueChangedFunction
        else:
            self.onValueChanged = lambda: None

    def _checkNewSelection(self, event):
        if not self.last_value == self.get():
            self.last_value = self.get()
            self.onValueChanged()

    def get(self) -> tuple:
        currentUnit = super().get()
        return currentUnit, self.units.getValue(currentUnit)


class GenericEntry(ttk.Entry):
    """
    TTK Entry that can take any string. Also has the usual callbacks for usage in PropertyLines.

    The Widget will validate the entered value upon unfocus or when calling get().
    If the value is a new string, it will call onValueChanged().
    """
    def __init__(self, master=None, defaultValue: str = "", *, onValueChangedFunction=None, **kwargs):
        # Register Tkinter-Validation
        validateWrapper = (master.register(self._validate), '%P')

        super().__init__(
            master,
            validate="focusout",
            validatecommand=validateWrapper,
            **kwargs  # Additional Keyword Arguments for Entries
        )

        # Set Defaults
        self.insert(0, defaultValue)
        self.last_value = defaultValue

        # Set onChanged Function
        if callable(onValueChangedFunction):
            self.onValueChanged = onValueChangedFunction
        else:
            self.onValueChanged = lambda: None

    def _validate(self, proposed_value: str) -> bool:
        # Only checks if value is new and always returns True (all strings are valid)
        if not (self.last_value == proposed_value):
            self.onValueChanged()
        self.last_value = proposed_value
        return True

    def get(self):
        # Validate on get() in case new input hasn't been validated yet because user is still focussed on this widget
        if self.focus_get() == self:
            self._validate(super().get())
        return super().get()


class ListCombobox(ttk.Combobox):
    """
    TTK Combobox that can select between different options in a list or dict.

    The Widget will fill the Combobox with all entries from the list or all keys in a dict in that order.
    When a selection is different from the previous it will call onValueChanged().
    """
    def __init__(self, master=None, options: list | dict = [""], defaultIndex: int = 0, *,
                 onValueChangedFunction=None, **kwargs):

        if type(options) == list:
            optionTuple = tuple(options)
            self.conversionDict = None
        elif type(options) == dict:
            optionTuple = tuple(options.keys())
            self.conversionDict = options

        super().__init__(
            master,
            values=optionTuple,
            state="readonly"
        )
        self.current(defaultIndex)
        self.last_value = self.get()
        self.bind("<<ComboboxSelected>>", self._checkNewSelection)

        # Set onChanged Function
        if callable(onValueChangedFunction):
            self.onValueChanged = onValueChangedFunction
        else:
            self.onValueChanged = lambda: None

    def _checkNewSelection(self, event):
        if not self.last_value == self.get():
            self.last_value = self.get()
            self.onValueChanged()

    def get(self):
        currentSelection = super().get()
        if self.conversionDict is not None:
            return self.conversionDict[currentSelection]
        else:
            return currentSelection