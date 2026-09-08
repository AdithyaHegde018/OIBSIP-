"""
gui.py
-------
Tkinter interface for the BMI Calculator.

This is the only module that "knows about" every other module. It reads
what the user typed, hands numbers off to bmi_calculator.py, hands
records off to database.py, and (from Phase 9) will hand data off to
chart.py. As of Phase 8: Calculate, Save, and View History are fully
wired; View BMI Chart is still a placeholder.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from bmi_calculator import calculate_bmi, get_category, validate_name, validate_weight, validate_height
from database import save_record, get_user_records, get_all_user_names
from chart import has_enough_records, build_bmi_trend_figure

WINDOW_TITLE = "BMI Calculator"
WINDOW_SIZE = "480x660"

# A small palette + font scheme kept in one place so the whole app looks
# consistent and is easy to tweak later.
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_LABEL = ("Segoe UI", 11)
FONT_ENTRY = ("Segoe UI", 11)
FONT_RESULT = ("Segoe UI", 14, "bold")
FONT_BUTTON = ("Segoe UI", 10)

BACKGROUND_COLOR = "#f4f6f8"
TEXT_COLOR = "#222222"

# Subtle, professional color-coding for the BMI category -- text color
# only, not a loud background, per the "no excessive decoration" spec.
CATEGORY_COLORS = {
    "Underweight": "#1f6fb2",   # calm blue
    "Normal": "#1e8449",        # calm green
    "Overweight": "#b9770e",    # muted amber
    "Obese": "#c0392b",         # muted red
}
DEFAULT_RESULT_COLOR = "#555555"  # neutral gray for the "--" placeholder state


class BMICalculatorApp:
    """Owns the main window and all of its widgets."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.resizable(False, False)
        self.root.configure(bg=BACKGROUND_COLOR)

        # Tkinter string variables backing the entry fields -- these let
        # us read/clear field values without digging into widget internals.
        self.name_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.height_var = tk.StringVar()

        # Holds the most recent successful calculation, e.g.
        # {"name": ..., "weight": ..., "height": ..., "bmi": ..., "category": ...}
        # so the Save Record button knows what to store.
        self.last_result = None

        # If the user edits any field after calculating, the previous
        # result no longer matches what's on screen -- invalidate it so
        # Save Record can never save stale/mismatched data.
        self.name_var.trace_add("write", self._invalidate_last_result)
        self.weight_var.trace_add("write", self._invalidate_last_result)
        self.height_var.trace_add("write", self._invalidate_last_result)

        self._build_widgets()

    def _build_widgets(self) -> None:
        """Build and place every widget in the window."""

        # ---- Title ----
        title_label = tk.Label(
            self.root, text="BMI CALCULATOR", font=FONT_TITLE,
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
        )
        title_label.pack(pady=(24, 12))

        # ---- Input form frame ----
        form_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        form_frame.pack(pady=5, padx=35, fill="x")

        self._add_field(form_frame, "Name", self.name_var, row=0)
        self._add_field(form_frame, "Weight (kg)", self.weight_var, row=1)
        self._add_field(form_frame, "Height (cm)", self.height_var, row=2)
        form_frame.columnconfigure(0, weight=1)

        # ---- Calculate button ----
        calculate_button = tk.Button(
            self.root,
            text="Calculate BMI",
            font=FONT_BUTTON,
            width=22,
            pady=4,
            command=self.on_calculate_clicked,
        )
        calculate_button.pack(pady=18)

        # ---- Separator ----
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=25)

        # ---- Result area ----
        result_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        result_frame.pack(pady=18)

        self.bmi_result_label = tk.Label(
            result_frame, text="BMI: --", font=FONT_RESULT,
            bg=BACKGROUND_COLOR, fg=DEFAULT_RESULT_COLOR,
        )
        self.bmi_result_label.pack()

        self.category_result_label = tk.Label(
            result_frame, text="Category: --", font=FONT_RESULT,
            bg=BACKGROUND_COLOR, fg=DEFAULT_RESULT_COLOR,
        )
        self.category_result_label.pack(pady=(6, 0))

        # ---- Separator ----
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=25, pady=12)

        # ---- Action buttons frame ----
        actions_frame = tk.Frame(self.root, bg=BACKGROUND_COLOR)
        actions_frame.pack(pady=5)

        ACTION_BUTTON_WIDTH = 17

        tk.Button(actions_frame, text="Save Record", font=FONT_BUTTON, width=ACTION_BUTTON_WIDTH,
                  command=self.on_save_clicked).grid(row=0, column=0, columnspan=2, pady=6)

        tk.Button(actions_frame, text="View History", font=FONT_BUTTON, width=ACTION_BUTTON_WIDTH,
                  command=self.on_view_history_clicked).grid(row=1, column=0, padx=6, pady=6)

        tk.Button(actions_frame, text="View BMI Chart", font=FONT_BUTTON, width=ACTION_BUTTON_WIDTH,
                  command=self.on_view_chart_clicked).grid(row=1, column=1, padx=6, pady=6)

        tk.Button(actions_frame, text="Clear", font=FONT_BUTTON, width=ACTION_BUTTON_WIDTH,
                  command=self.on_clear_clicked).grid(row=2, column=0, padx=6, pady=6)

        tk.Button(actions_frame, text="Exit", font=FONT_BUTTON, width=ACTION_BUTTON_WIDTH,
                  command=self.root.quit).grid(row=2, column=1, padx=6, pady=6)

    def _add_field(self, parent: tk.Frame, label_text: str, variable: tk.StringVar, row: int) -> None:
        """
        Helper to add one label + entry row, so the three fields stay
        consistent. Each field takes two grid rows (label, then entry)
        so widgets never overlap.
        """
        label_row = row * 2
        entry_row = row * 2 + 1

        label = tk.Label(
            parent, text=label_text, font=FONT_LABEL, anchor="w",
            bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
        )
        label.grid(row=label_row, column=0, sticky="w", pady=(10, 3))

        entry = tk.Entry(parent, textvariable=variable, font=FONT_ENTRY, relief="solid", bd=1)
        entry.grid(row=entry_row, column=0, sticky="ew", ipady=4, pady=(0, 4))

    # ------------------------------------------------------------------
    # Button handlers (placeholders for now -- wired up in later phases)
    # ------------------------------------------------------------------

    def _invalidate_last_result(self, *_args) -> None:
        """Clear the stored calculation whenever an input field changes."""
        self.last_result = None

    def on_calculate_clicked(self) -> None:
        """
        Validate the form, calculate BMI, and update the result labels.
        Never raises -- any problem is shown as a friendly popup instead.
        """
        name = self.name_var.get()
        name_error = validate_name(name)
        if name_error:
            messagebox.showerror("Invalid Input", name_error)
            return

        weight, weight_error = validate_weight(self.weight_var.get())
        if weight_error:
            messagebox.showerror("Invalid Input", weight_error)
            return

        height, height_error = validate_height(self.height_var.get())
        if height_error:
            messagebox.showerror("Invalid Input", height_error)
            return

        try:
            bmi = calculate_bmi(weight, height)
        except ValueError as error:
            # calculate_bmi() re-checks >0 itself, so this is a safety net
            # in case validate_number's rules and calculate_bmi's rules
            # ever drift apart.
            messagebox.showerror("Invalid Input", str(error))
            return

        category = get_category(bmi)

        self.bmi_result_label.config(text=f"BMI: {bmi:.2f}", fg=CATEGORY_COLORS.get(category, TEXT_COLOR))
        self.category_result_label.config(text=f"Category: {category}", fg=CATEGORY_COLORS.get(category, TEXT_COLOR))

        self.last_result = {
            "name": name.strip(),
            "weight": weight,
            "height": height,
            "bmi": bmi,
            "category": category,
        }

    def on_save_clicked(self) -> None:
        """
        Save the most recent calculation to the database.

        Requires a successful Calculate first -- self.last_result is None
        until on_calculate_clicked() has run without errors, and is reset
        to None whenever the fields are edited or cleared, so this can
        never save stale or mismatched data.
        """
        if self.last_result is None:
            messagebox.showwarning(
                "Nothing to Save",
                "Please calculate a BMI first before saving a record.",
            )
            return

        result = self.last_result
        success, error_message = save_record(
            result["name"], result["weight"], result["height"],
            result["bmi"], result["category"],
        )

        if success:
            messagebox.showinfo(
                "Record Saved",
                f"Saved a record for {result['name']} "
                f"(BMI {result['bmi']:.2f}, {result['category']}).",
            )
        else:
            messagebox.showerror("Save Failed", error_message)

    def on_view_history_clicked(self) -> None:
        """Open the BMI history window."""
        HistoryWindow(self.root)

    def on_view_chart_clicked(self) -> None:
        """Open the BMI trend chart window."""
        ChartWindow(self.root)

    def on_clear_clicked(self) -> None:
        """Clears all input fields, the result area, and the last calculation."""
        self.name_var.set("")
        self.weight_var.set("")
        self.height_var.set("")
        self.bmi_result_label.config(text="BMI: --", fg=DEFAULT_RESULT_COLOR)
        self.category_result_label.config(text="Category: --", fg=DEFAULT_RESULT_COLOR)
        self.last_result = None


class HistoryWindow:
    """
    A separate pop-up window showing saved BMI records for a selected
    user, using a ttk.Treeview table. Opened fresh each time "View
    History" is clicked, so it always starts with the latest user list.
    """

    COLUMNS = ("name", "weight", "height", "bmi", "category", "date")
    HEADINGS = {
        "name": "Name", "weight": "Weight", "height": "Height",
        "bmi": "BMI", "category": "Category", "date": "Date",
    }

    def __init__(self, parent: tk.Tk):
        self.window = tk.Toplevel(parent)
        self.window.title("BMI History")
        self.window.configure(bg=BACKGROUND_COLOR)

        # Position the window near the main app window instead of relying
        # on the window manager's default placement (which can otherwise
        # put it off-screen or awkwardly far from the main window).
        parent.update_idletasks()
        x = parent.winfo_x() + 40
        y = parent.winfo_y() + 40
        self.window.geometry(f"560x420+{x}+{y}")

        tk.Label(self.window, text="BMI HISTORY", font=FONT_TITLE, bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=(15, 10))

        self.user_names = get_all_user_names()

        if not self.user_names:
            # No one has saved a record yet -- show a friendly message
            # instead of an empty, confusing table.
            tk.Label(
                self.window,
                text="No records found yet.\nCalculate a BMI and click 'Save Record' first.",
                font=FONT_LABEL, justify="center",
            ).pack(pady=40)
            return

        # ---- User selection row ----
        selector_frame = tk.Frame(self.window)
        selector_frame.pack(pady=5)

        tk.Label(selector_frame, text="Select user:", font=FONT_LABEL).pack(side="left", padx=(0, 8))

        self.selected_user = tk.StringVar(value=self.user_names[0])
        self.user_dropdown = ttk.Combobox(
            selector_frame, textvariable=self.selected_user,
            values=self.user_names, state="readonly", width=20,
        )
        self.user_dropdown.pack(side="left")
        self.user_dropdown.bind("<<ComboboxSelected>>", lambda _event: self._load_records())

        tk.Button(selector_frame, text="Refresh", font=FONT_BUTTON,
                  command=self._refresh).pack(side="left", padx=10)

        # ---- Treeview table ----
        table_frame = tk.Frame(self.window)
        table_frame.pack(pady=10, padx=15, fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=self.COLUMNS, show="headings", height=10)
        for column in self.COLUMNS:
            self.tree.heading(column, text=self.HEADINGS[column])
            self.tree.column(column, width=85, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # ---- Empty-state message (shown/hidden depending on results) ----
        self.empty_label = tk.Label(self.window, text="", font=FONT_LABEL, fg="gray")
        self.empty_label.pack(pady=(0, 10))

        self._load_records()

    def _refresh(self) -> None:
        """Reload the user list (in case new records were saved) and the table."""
        self.user_names = get_all_user_names()
        self.user_dropdown.configure(values=self.user_names)
        if self.user_names and self.selected_user.get() not in self.user_names:
            self.selected_user.set(self.user_names[0])
        self._load_records()

    def _load_records(self) -> None:
        """Clear and repopulate the table for the currently selected user."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        user_name = self.selected_user.get()
        records = get_user_records(user_name)

        if not records:
            self.empty_label.config(text=f"No records found for {user_name}.")
            return

        self.empty_label.config(text="")
        for record in records:
            self.tree.insert("", "end", values=(
                record["user_name"],
                record["weight"],
                record["height"],
                f"{record['bmi']:.2f}",
                record["category"],
                record["recorded_at"],
            ))


class ChartWindow:
    """
    A separate pop-up window showing a BMI trend chart for a selected
    user, using a Matplotlib figure built by chart.py and embedded via
    FigureCanvasTkAgg. Same structure as HistoryWindow: pick a user from
    a dropdown, chart updates automatically.
    """

    def __init__(self, parent: tk.Tk):
        self.window = tk.Toplevel(parent)
        self.window.title("BMI Trend Chart")
        self.window.configure(bg=BACKGROUND_COLOR)

        parent.update_idletasks()
        x = parent.winfo_x() + 60
        y = parent.winfo_y() + 60
        self.window.geometry(f"620x520+{x}+{y}")

        tk.Label(self.window, text="BMI TREND CHART", font=FONT_TITLE, bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=(15, 10))

        self.user_names = get_all_user_names()

        if not self.user_names:
            tk.Label(
                self.window,
                text="No records found yet.\nCalculate a BMI and click 'Save Record' first.",
                font=FONT_LABEL, justify="center",
            ).pack(pady=40)
            return

        # ---- User selection row ----
        selector_frame = tk.Frame(self.window)
        selector_frame.pack(pady=5)

        tk.Label(selector_frame, text="Select user:", font=FONT_LABEL).pack(side="left", padx=(0, 8))

        self.selected_user = tk.StringVar(value=self.user_names[0])
        self.user_dropdown = ttk.Combobox(
            selector_frame, textvariable=self.selected_user,
            values=self.user_names, state="readonly", width=20,
        )
        self.user_dropdown.pack(side="left")
        self.user_dropdown.bind("<<ComboboxSelected>>", lambda _event: self._load_chart())

        tk.Button(selector_frame, text="Refresh", font=FONT_BUTTON,
                  command=self._refresh).pack(side="left", padx=10)

        # ---- Chart area (a placeholder frame; the canvas widget inside
        # it is replaced every time a new chart is drawn) ----
        self.chart_container = tk.Frame(self.window)
        self.chart_container.pack(pady=10, padx=15, fill="both", expand=True)
        self.canvas_widget = None

        self._load_chart()

    def _refresh(self) -> None:
        """Reload the user list (in case new records were saved) and the chart."""
        self.user_names = get_all_user_names()
        self.user_dropdown.configure(values=self.user_names)
        if self.user_names and self.selected_user.get() not in self.user_names:
            self.selected_user.set(self.user_names[0])
        self._load_chart()

    def _load_chart(self) -> None:
        """Draw (or redraw) the trend chart for the currently selected user."""
        # Remove any previously drawn chart/message before showing the new one.
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        user_name = self.selected_user.get()
        records = get_user_records(user_name)

        if not has_enough_records(records):
            tk.Label(
                self.chart_container,
                text=(
                    f"{user_name} needs at least 2 saved records to show a "
                    f"trend.\nCurrently has {len(records)}."
                ),
                font=FONT_LABEL, justify="center",
            ).pack(pady=40)
            return

        figure = build_bmi_trend_figure(user_name, records)
        canvas = FigureCanvasTkAgg(figure, master=self.chart_container)
        canvas.draw()
        self.canvas_widget = canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)
