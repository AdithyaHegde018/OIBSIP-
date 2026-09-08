"""
main.py
--------
Entry point for the BMI Calculator application.

This file intentionally contains almost no logic -- it just creates the
Tkinter root window and hands control over to BMICalculatorApp in gui.py.
"""

import tkinter as tk

from database import create_database
from gui import BMICalculatorApp


def main() -> None:
    create_database()
    root = tk.Tk()
    app = BMICalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
