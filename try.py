import serial

arduino = serial.Serial(port='COM6', baudrate=9600, timeout=1)
while True:
    data = arduino.readline().decode('utf-8').strip()
    print(data)
