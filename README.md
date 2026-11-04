# ISKApp

ISKApp is a Flask web application that combines a BMI calculator and health-record tracker with live Arduino sensor monitoring. It was my first full-stack web application, built to learn how a Python web framework, a database and hardware input fit together in one project.

## Features

- **User accounts** — signup and login. Passwords are stored only as salted hashes in the database (Werkzeug); plain-text passwords are never stored
- **BMI calculator** — enter name, age, gender, weight and height to get a BMI value and category (Underweight / Normal / Overweight / Obese), with optional image upload
- **BMI history** — every calculation is saved to the database and listed in a history page
- **CSV export** — download the full BMI history as a CSV file
- **Arduino integration** — reads live sound-sensor data over a serial connection and displays it, and can send commands back to the board. If the Arduino is not connected, the app falls back to the last sensor value instead of crashing
- **Progressive Web App support** — web app manifest and service worker are served by the app

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **Hardware:** Arduino over serial (`pyserial`, sketch in `arduino/sound.ino`)
- **Frontend:** HTML and CSS (Jinja2 templates)

## Getting Started

### Prerequisites

- Python 3.9+
- Optional: an Arduino board running `arduino/sound.ino`, connected to serial port `COM6` (the port is set in `app.py` — change it to match your machine)

### Installation

```bash
git clone https://github.com/IskandarAbdullah/ISKApp.git
cd ISKApp
pip install -r requirements.txt
```

### Run

```bash
python app.py
```

Then open http://localhost:5000 in your browser. The SQLite database (`bmi_history.db`) and its tables — including the user accounts table — are created automatically on first run.

## Usage

1. **Sign up** on the signup page, then log in
2. **Calculate your BMI** on the BMI page and, optionally, attach an image
3. **View history** to see all saved BMI records, or export them as CSV
4. **Open the Arduino / IoT pages** to see live sensor values when a board is connected

## Project Structure

```text
ISKApp/
├── app.py              # Flask application — routes, models, Arduino helpers
├── requirements.txt    # Python dependencies
├── arduino/
│   └── sound.ino       # Arduino sketch for the sound sensor
├── templates/          # Jinja2 HTML templates (home, signup, BMI, history, Arduino, ...)
├── static/             # Static assets, uploads, PWA manifest and service worker
└── README.md
```

## Notes

- Running the app will create local files that should not be committed — the SQLite database, `__pycache__/` and the `instance/` folder are covered by `.gitignore`.
- User accounts created by older versions of this app were stored in a plain-text file. That storage was removed for security reasons; accounts from those versions need to sign up again.

## Author

**Iskandar Abdullah** — [@IskandarAbdullah](https://github.com/IskandarAbdullah)
