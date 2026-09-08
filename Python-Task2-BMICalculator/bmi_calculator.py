"""
bmi_calculator.py
-------------------
Pure BMI logic: calculation, categorization, and input validation.

This module has NO knowledge of Tkinter or SQLite on purpose — it only
deals with numbers in and numbers/strings out. That makes it trivial to
test on its own (see the manual tests at the bottom of this docstring)
and easy to reuse if the GUI ever changes.

Manual test (run from a Python shell in this folder):
    >>> from bmi_calculator import calculate_bmi, get_category
    >>> calculate_bmi(65, 170)
    22.49
    >>> get_category(22.49)
    'Normal'
"""

# BMI category thresholds, kept as named constants instead of "magic
# numbers" scattered through the code -- easy to explain, easy to change.
UNDERWEIGHT_MAX = 18.5
NORMAL_MAX = 24.9
OVERWEIGHT_MAX = 29.9


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """
    Calculate BMI from weight in kilograms and height in centimetres.

    Formula: BMI = weight (kg) / height (m)^2
    Height is converted from centimetres to metres before the calculation.

    Returns the BMI rounded to 2 decimal places.

    Raises ValueError if weight or height is not greater than zero --
    the caller (gui.py) is expected to catch this and show a friendly
    message instead of letting the app crash.
    """
    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")
    if height_cm <= 0:
        raise ValueError("Height must be greater than zero.")

    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)


def get_category(bmi: float) -> str:
    """
    Map a BMI value to its standard health category.

        BMI < 18.5        -> Underweight
        18.5 - 24.9        -> Normal
        25.0 - 29.9         -> Overweight
        BMI >= 30            -> Obese
    """
    if bmi < UNDERWEIGHT_MAX:
        return "Underweight"
    if bmi <= NORMAL_MAX:
        return "Normal"
    if bmi <= OVERWEIGHT_MAX:
        return "Overweight"
    return "Obese"


def validate_name(name: str) -> str | None:
    """Return an error message if `name` is invalid, otherwise None."""
    if not name or not name.strip():
        return "Please enter your name."
    return None


def validate_number(
    value_text: str,
    field_label: str,
    min_realistic: float | None = None,
    max_realistic: float | None = None,
) -> tuple[float | None, str | None]:
    """
    Validate a numeric text field (weight or height entered as a string
    from a Tkinter Entry widget).

    Returns a (value, error_message) tuple:
        * On success: (float_value, None)
        * On failure: (None, "friendly error message")

    `field_label` is used to build a friendly message, e.g. "weight" or
    "height", so this one function covers both fields.

    `min_realistic`/`max_realistic` are optional bounds beyond "greater
    than zero" -- used to catch technically-positive but nonsensical
    input like a height of 5 cm or a weight of 999999 kg.
    """
    if not value_text or not value_text.strip():
        return None, f"Please enter a valid {field_label}."

    try:
        value = float(value_text.strip())
    except ValueError:
        return None, f"Please enter a valid {field_label}."

    if value <= 0:
        return None, f"{field_label.capitalize()} must be greater than zero."

    if min_realistic is not None and value < min_realistic:
        return None, (
            f"That {field_label} looks unrealistically low. "
            f"Please double-check and try again."
        )
    if max_realistic is not None and value > max_realistic:
        return None, (
            f"That {field_label} looks unrealistically high. "
            f"Please double-check and try again."
        )

    return value, None


def validate_weight(value_text: str) -> tuple[float | None, str | None]:
    """Validate a weight field with a realistic human range (1-500 kg)."""
    return validate_number(value_text, "weight", min_realistic=1, max_realistic=500)


def validate_height(value_text: str) -> tuple[float | None, str | None]:
    """Validate a height field with a realistic human range (30-300 cm)."""
    return validate_number(value_text, "height", min_realistic=30, max_realistic=300)
