from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import serial, time, re, os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bmi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class BMIRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    bmi = db.Column(db.Float)
    category = db.Column(db.String(20))
    image_path = db.Column(db.String(200))

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

        # Save to database
        record = BMIRecord(
            name=name,
            age=age,
            gender=gender,
            weight=weight,
            height=height,
            bmi=round(bmi_value, 2),
            category=category,
            image_path=image_path
        )
        db.session.add(record)
        db.session.commit()

        return render_template("bmi.html",
                               name=name, age=age, gender=gender,
                               weight=weight, height=height,
                               bmi=round(bmi_value, 2), category=category,
                               image_path=image_path)
    return render_template("bmi.html")

@app.route('/bmi_history')
def bmi_history():
    records = BMIRecord.query.all()
    return render_template('bmi_history.html', records=records)

@app.route('/download_history')
def download_history():
    import csv
    from io import StringIO
    from flask import send_file
    
    records = BMIRecord.query.all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Age', 'Gender', 'Weight (kg)', 'Height (cm)', 'BMI', 'Category'])
    
    for record in records:
        writer.writerow([
            record.id,
            record.name,
            record.age,
            record.gender,
            record.weight,
            record.height,
            record.bmi,
            record.category
        ])
    
    output.seek(0)
    
    from io import BytesIO
    bytes_output = BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8'))
    bytes_output.seek(0)
    
    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name='bmi_history.csv'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
