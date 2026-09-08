# BMI Calculator (Advanced)

A professional, desktop BMI (Body Mass Index) Calculator built with Python
and Tkinter. Users can enter their name, weight, and height, calculate
their BMI and health category, save records over time, browse their
history in a searchable table, and view a BMI trend chart.

## Oasis Infobyte Internship

This project was developed as part of the **Oasis Infobyte Python
Programming Internship (OIBSIP)**.

**Task:** Task 2 — BMI Calculator

---

## Features

### Beginner features
- Enter name, weight (kg), and height (cm)
- Calculate BMI using the standard formula
- Display BMI rounded to 2 decimal places
- Display the correct health category (Underweight / Normal / Overweight / Obese)
- Strong input validation with friendly error messages
- The app never crashes on invalid input

### Advanced features
- **Local SQLite storage** — records persist across sessions
- **Multi-user support** — any number of named users, each with their own history
- **BMI History window** — a `ttk.Treeview` table, filterable by user, with a Refresh button
- **BMI Trend Chart** — a Matplotlib line chart of BMI over time per user, embedded directly in a Tkinter window
- **Category-based visual feedback** — the result area is subtly color-coded per category (calm blue/green/amber/red — no excessive decoration)
- **Realistic-range validation** — catches technically-positive but nonsensical input (e.g. a height of 5 cm)
- **Stale-data protection** — editing a field after calculating invalidates the result, so Save Record can never save a mismatched BMI
- Graceful handling of missing/invalid database paths, empty history, and insufficient chart data

---

## Technology stack

| Purpose | Library |
|---|---|
| GUI | `tkinter` (standard library) |
| Local database | `sqlite3` (standard library) |
| Trend chart | `matplotlib` |

---

## BMI formula

```
BMI = weight (kg) / height (m)²
```

Height is entered in centimetres and converted to metres internally
(`height_m = height_cm / 100`) before the calculation. The result is
rounded to 2 decimal places.

## BMI categories

| BMI range | Category |
|---|---|
| < 18.5 | Underweight |
| 18.5 – 24.9 | Normal |
| 25.0 – 29.9 | Overweight |
| ≥ 30.0 | Obese |

---

## Project architecture

```
Python-Task2-BMICalculator/
│
├── main.py               # Entry point — creates the database, launches the GUI
├── gui.py                # All Tkinter windows: main app, History window, Chart window
├── bmi_calculator.py      # Pure logic: calculate_bmi(), get_category(), validation
├── database.py            # All SQLite access: create/save/fetch records
├── chart.py               # Builds the Matplotlib trend figure (no Tkinter knowledge)
├── requirements.txt
├── .gitignore
├── README.md
│
└── screenshots/
```

**Design principle:** logic and Tkinter are kept separate. `bmi_calculator.py`,
`database.py`, and `chart.py` have zero knowledge of Tkinter, so each can
be tested independently from a plain Python shell. `gui.py` is the only
module that "knows about" every other module — it's the coordinator.

**Data flow:** `main.py` creates the database and launches `gui.py`'s
main window → user fills the form → `gui.py` validates via
`bmi_calculator.py` → calculates via `bmi_calculator.py` → optionally
saves via `database.py` → History/Chart windows read back via
`database.py` and (for the chart) render via `chart.py`.

---

## Installation

### 1. Requirements
- Python 3.10 or newer
- Tkinter (bundled with most Python installations; on some Linux
  distributions you may need `sudo apt-get install python3-tk`)

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## How to run the project

```bash
python main.py
```

The database file `bmi_calculator.db` is created automatically in the
project folder the first time you run the app.

---

## How to calculate BMI

1. Enter your **Name**, **Weight (kg)**, and **Height (cm)**.
2. Click **Calculate BMI**.
3. The BMI and category appear below, color-coded by category.
4. If any field is missing, non-numeric, zero, negative, or unrealistic
   (e.g. a height of 5 cm), a clear popup explains what to fix — the
   app never crashes on bad input.

## How to save records

1. Calculate a BMI first (Save Record is disabled in effect until a
   valid calculation exists).
2. Click **Save Record**.
3. A confirmation popup shows the name, BMI, and category that were saved.
4. If you edit any field afterward without recalculating, Save Record
   will ask you to calculate again — this prevents saving a result that
   no longer matches what's on screen.

## How to view history

1. Click **View History**.
2. Pick a user from the dropdown — the table shows every saved record
   for that user (weight, height, BMI, category, date).
3. Click **Refresh** if you've just saved a new record and want the
   list/table to reflect it.
4. If no records exist yet, a friendly message explains that instead of
   showing an empty table.

## How to view charts

1. Click **View BMI Chart**.
2. Pick a user from the dropdown.
3. If the user has 2 or more saved records, a line chart appears showing
   BMI over time (date on the X-axis, BMI on the Y-axis).
4. If the user has fewer than 2 records, a message explains that more
   records are needed — the app never draws a misleading single-point trend.

---

## Database explanation

- **File:** `bmi_calculator.db` (SQLite), created automatically on first run.
- **Table:** `bmi_records`
  - `id` — auto-incrementing primary key
  - `user_name` — the name entered on the form
  - `weight`, `height`, `bmi` — numeric values
  - `category` — the health category at the time of saving
  - `recorded_at` — date and time the record was saved (`DD-MM-YYYY HH:MM`)
- All database access goes through `database.py`; no other module ever
  imports `sqlite3` directly.
- The database is entirely local — nothing is ever sent over the network.

---

## Error handling

The application is designed to never crash. It handles, with clear
messages instead of tracebacks:

- Empty, non-numeric, negative, zero, or unrealistic weight/height input
- Empty name (including whitespace-only)
- Missing or unwritable database path
- Empty history for a user (or no users at all yet)
- Insufficient records for a meaningful trend chart
- Saving stale data after editing a field without recalculating

---

## Screenshots

Add screenshots of the running application to the `screenshots/` folder,
for example:
- `main_window.png`
- `bmi_result_categories.png`
- `history_window.png`
- `bmi_chart.png`
- `invalid_input_popup.png`

---

## Testing checklist

```
[x] Valid BMI calculation
[x] Underweight
[x] Normal
[x] Overweight
[x] Obese
[x] Empty name
[x] Empty weight
[x] Empty height
[x] Text in weight
[x] Text in height
[x] Negative weight
[x] Negative height
[x] Zero weight
[x] Zero height
[x] Save record
[x] Multiple users
[x] Multiple records for one user
[x] View history
[x] Empty history
[x] View BMI chart
[x] Only one record
[x] Multiple BMI records
[x] Database creation
[x] Database error handling
[x] Clear button
[x] Exit button
```

---

## Future improvements

- Export history to CSV or PDF
- Support for BMI in imperial units (lbs/inches)
- Editable/deletable records in the History window
- A settings screen for custom category thresholds (e.g. age/sex-adjusted ranges)
- Package as a standalone executable (PyInstaller) for easier distribution

---

## Author

Built by Adithya, as part of the **Oasis Infobyte Python Programming
Internship (OIBSIP)** — Task 2: BMI Calculator.
