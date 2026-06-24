from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import serial, time, re, os

app = Flask(__name__)

arduino = None
last_value = "0"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def connect_arduino():
    global arduino
    if not arduino or not arduino.is_open:
        try:
            arduino = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)
            time.sleep(2)
        except Exception:
            arduino = None
    return arduino

def read_data():
    global last_value
    conn = connect_arduino()
    if conn and conn.is_open:
        try:
            raw = conn.readline().decode('utf-8', errors='ignore').strip()
            if raw.isdigit():
                last_value = raw
                return raw
            else:
                return last_value
        except Exception:
            return last_value
    else:
        return last_value
    
def send_command(command):
    conn = connect_arduino()
    if conn and conn.is_open:
        try:
            conn.write((command + "\n").encode())
            return f"Sent: {command}"
        except Exception:
            return "Error sending command"
    else:
        return "Arduino not connected"

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/arduino')
def arduino_data():
    value = read_data()
    return render_template('arduino.html', sensor_value=value)

@app.route('/arduino_raw')
def arduino_raw():
    return read_data()

@app.route('/send/<command>')
def send_command_route(command):
    return send_command(command)

@app.route('/main')
def mainpage():
    user_name = request.args.get('name')
    return render_template('main.html', name=user_name)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        with open("users.txt", "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    saved_name, saved_pass = parts
                    if saved_name == name:
                        return render_template('error.html')
        with open("users.txt", "a") as file:
            file.write(f"{name},{password}\n")
    return render_template('signup.html')

@app.route('/get_name', methods=['GET', 'POST'])
def get_name():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        with open("users.txt", "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    saved_name, saved_pass = parts
                    if name == saved_name and password == saved_pass:
                        return redirect(url_for('mainpage', name=name))
        return render_template('error.html')

@app.route('/bmi', methods=['GET', 'POST'])
def bmi():
    if request.method == 'POST':
        name = request.form.get("name")
        age = int(request.form.get("age"))
        gender = request.form.get("gender")
        weight = float(request.form.get("weight"))
        height = float(request.form.get("height"))

        bmi_value = weight / ((height / 100) ** 2)

        if bmi_value < 18.5:
            category = "Underweight"
        elif bmi_value < 25:
            category = "Normal"
        elif bmi_value < 30:
            category = "Overweight"
        else:
            category = "Obese"

        image = request.files.get("image")
        image_path = None
        if image:
            filename = image.filename
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_path = url_for('static', filename=f'uploads/{filename}')

        return render_template("bmi.html",
                               name=name, age=age, gender=gender,
                               weight=weight, height=height,
                               bmi=round(bmi_value, 2), category=category,
                               image_path=image_path)
    return render_template("bmi.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
