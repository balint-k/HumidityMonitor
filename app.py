import csv
import os
import time
import threading
from sensor import Sensor
from datetime import datetime
from collections import deque
import flask

LENGHT = 3 * 24 * 12 # 3 days of data at 5-minute intervals

class DataHandler:
    def __init__(self, length:int = 100 ):
        self.lenght = length
        self.readData()

    def readData(self):
        self.data = deque(maxlen=self.lenght)

        if  os.path.exists('data.csv'):
            with open('data.csv', 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    row = [row[0], float(row[1]), float(row[2])]
                    self.data.append(row)

    def writeData(self):
        for i in range(3):
            try:
                with open('data.csv', 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["TimeStamp", "Humidity", "Temperature"])
                    for row in self.data:
                        writer.writerow(row)
            except Exception as e:
                time.sleep(1)
            else:
                break

    def appendData(self, humidity, temperature):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.data.append([timestamp, humidity, temperature])

class Watcher:
    def __init__(self):
        self.sensor = Sensor()
        self.dataBase = DataHandler(LENGHT)


    def run(self):
        thread = threading.Thread(target=self.mainLoop)
        thread.daemon = True
        thread.start()

    def mainLoop(self):
        while True:
            for i in range(3):
                humidity, temperature = self.sensor.read()
                if humidity is not None and temperature is not None:
                    self.dataBase.appendData(humidity, temperature)
                    self.dataBase.writeData()
                    break
                else:
                    time.sleep(1)
            time.sleep(300)  # Wait for 5 minutes

class Monitor:
    def __init__(self):
        self.app = flask.Flask(__name__)
        self.watcher = Watcher()
        self.watcher.run()
        self.setupRoutes()
        self.app.run(host='0.0.0.0', port=8040)

    def setupRoutes(self):
        @self.app.route('/')
        def index():
            data = list(self.watcher.dataBase.data)
            temperature = self.watcher.dataBase.data[-1][2]
            humidity = self.watcher.dataBase.data[-1][1]
            lastReadingTime = self.watcher.dataBase.data[-1][0]
            return flask.render_template('index.html', data=data, temperature=temperature, humidity=humidity, lastReadingTime=lastReadingTime)
        


Monitor()