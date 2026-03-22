import csv
import os
import time
import threading
from sensor import SensorHandler
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
                    row = [row[0], float(row[1]), float(row[2])], float(row[3]), float(row[4]), float(row[5])
                    self.data.append(row)

    def writeData(self):
        with open('data.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["TimeStamp", "HumidityDHT11", "TemperatureDHT11", "HumidityBM280", "TemperatureBM280", "PressureBM280"])
            for row in self.data:
                writer.writerow(row)


    def appendData(self, dataRow: list):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dataRow.insert(0,timestamp)
        self.data.append(dataRow)

class Watcher:
    def __init__(self):
        self.sensors = SensorHandler()
        self.dataBase = DataHandler(LENGHT)


    def run(self):
        thread = threading.Thread(target=self.mainLoop)
        thread.daemon = True
        thread.start()

    def mainLoop(self):
        while True:
            dataRow = self.sensors.read()
            self.dataBase.appendData(dataRow)
            self.dataBase.writeData()
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
            temperature = self.watcher.dataBase.data[-1][4]
            humidity = self.watcher.dataBase.data[-1][3]
            lastReadingTime = self.watcher.dataBase.data[-1][0]
            return flask.render_template('index.html', data=data, temperature=temperature, humidity=humidity, lastReadingTime=lastReadingTime)
        


Monitor()