import time
import smbus

def smbusWrapper(func):
    bus = smbus.SMBus(1)
    returnValue = func(bus)
    bus.close()
    return returnValue


class SMBus:
    CHANNEL = 1 # setup, van másik i2c is 

    def __init__(self):
        self.bus = None

    def __enter__(self):
        self.bus = smbus.SMBus(self.CHANNEL)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bus.close()

class Sensor_BM280:
    ID = 96 # bosch datasheet
    REGISTER_ID = 0xD0 
    ADDRESS = 0x76

    def __init__(self):
        self.available = self.verifySensor()
        
    def verifySensor(self) -> bool:
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_ID)
        return registryContent == self.ID

class Sensor_DHT11:
    PIN = 7 
    SAMPLE_TIME = 10 / 1000 / 1000

    def __init__(self):
        pass

    def read(self):
        pass


class SensorHandler:
    def __init__(self):
        pass
        #self.dht11Device = adafruit_dht.DHT11(board.D4)
        #self.bm280Device = Sensor_BM280()

    def read(self):
        try:
            #temperature1 = self.dhtDevice.temperature
            #humidity1 = self.dhtDevice.humidity
            return [10, 20, 11, 21, 110000]
        except RuntimeError as error:
            print(error.args[0])
            return None, None