"""
chart.py
---------
Builds a BMI trend chart using Matplotlib.

This module has NO knowledge of Tkinter -- it only builds and returns a
matplotlib Figure object. gui.py is responsible for embedding that
Figure into a window (via FigureCanvasTkAgg). This keeps the plotting
logic testable on its own, without needing a GUI to run.
"""

from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")  # Safe default backend; gui.py switches the canvas
                        # to TkAgg embedding when it displays the figure.
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

MIN_RECORDS_FOR_TREND = 2
DATE_FORMAT = "%d-%m-%Y %H:%M"  # matches database.py's recorded_at format


def has_enough_records(records: list[dict]) -> bool:
    """A trend needs at least 2 points to mean anything."""
    return len(records) >= MIN_RECORDS_FOR_TREND


def build_bmi_trend_figure(user_name: str, records: list[dict]) -> plt.Figure:
    """
    Build and return a Matplotlib Figure showing BMI over time for one user.

    `records` is expected to be the list of dicts returned by
    database.get_user_records() -- already ordered oldest-first, each
    with at least "bmi" and "recorded_at" keys.

    Caller is responsible for checking has_enough_records() first; this
    function assumes there are at least 2 records.
    """
    dates = [datetime.strptime(r["recorded_at"], DATE_FORMAT) for r in records]
    bmi_values = [r["bmi"] for r in records]

    figure = plt.Figure(figsize=(6, 4.5), dpi=100)
    axes = figure.add_subplot(111)

    axes.plot(dates, bmi_values, marker="o", linestyle="-", color="#2a6fdb")

    axes.set_title(f"BMI Trend — {user_name}")
    axes.set_xlabel("Date")
    axes.set_ylabel("BMI")
    axes.grid(True, alpha=0.3)

    # Readable date labels instead of raw datetime strings crowding the axis.
    axes.xaxis.set_major_formatter(mdates.DateFormatter("%d-%m-%Y"))
    figure.autofmt_xdate(rotation=30)

    # If all records were saved within the same short window (e.g. testing
    # by saving several records back-to-back), Matplotlib's date
    # autoscaling can pick a misleadingly wide multi-year range. Give the
    # axis a small fixed padding in that case so points stay readable.
    span = max(dates) - min(dates)
    if span < timedelta(hours=1):
        padding = timedelta(hours=12)
        axes.set_xlim(min(dates) - padding, max(dates) + padding)

    figure.tight_layout()
    return figure
