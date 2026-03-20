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
        return self.bus

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.bus.close()

class Sensor_BM280:
    ID = 96 # bosch datasheet
    ADDRESS = 0x76

    REGISTER_ID = 0xD0 
    REGISTER_CTRL_HUM = 0xF2
    REGISTER_STATUS = 0xF3
    REGISTER_CTRL_MEAS = 0xF4
    REGISTER_CONFIG = 0xF5
    REGISTER_PRESS_MSB = 0xF7
    REGISTER_PRESS_LSB = 0xF8
    REGISTER_PRESS_XLSB = 0xF9
    REGISTER_TEMP_MSB = 0xFA
    REGISTER_TEMP_LSB = 0xFB
    REGISTER_TEMP_XLSB = 0xFC
    REGISTER_HUM_MSB = 0xFD
    REGISTER_HUM_LSB = 0xFE

    REGISTER_digT1_MSB = 0x89
    REGISTER_digT1_LSB = 0x88
    REGISTER_digT2_MSB = 0x8B
    REGISTER_digT2_LSB = 0x8A
    REGISTER_digT3_MSB = 0x8D
    REGISTER_digT3_LSB = 0x8C


    def __init__(self):
        self.available = self.verifySensor()
        if self.available:
            self.enableTemperatureMeasurement()

    def exit(self):
        self.available = self.verifySensor()
        if self.available:
            self.disableTemperatureMeasurement()

        
    def verifySensor(self) -> bool:
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_ID)
        return registryContent == self.ID

    def triggerMeasurement(self):
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            message = registryContent | 0b00000001
            bus.write_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS, message)
            
            status = 1
            while status != 0:
                status = bus.read_byte_data(self.ADDRESS, self.REGISTER_STATUS)
                status = status & 0b00001000
                time.sleep(0.01)

    def enableTemperatureMeasurement(self):
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            message = registryContent | 0b01000000 # 010 oversampling x2
            bus.write_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS, message)
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            masked = registryContent & 0b01000000
            if masked == 0:
                raise ValueError("Temperature measurement can\'t be enabled")

    def disableTemperatureMeasurement(self):
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            message = registryContent & 0b00011111 
            bus.write_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS, message)
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            masked = registryContent & 0b11100000
            if masked != 0:
                raise ValueError("Temperature measurement can\'t be disabled")

    def getTemperature(self):
        with SMBus() as bus:
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_TEMP_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_TEMP_LSB)
            package3 = bus.read_byte_data(self.ADDRESS, self.REGISTER_TEMP_XLSB)

            adc_T = package1 << 12 | package2 << 4 | package3 >> 4


            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digT1_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digT1_LSB)
            dig_T1 = package1 << 8 | package2

            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digT2_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digT2_LSB)
            dig_T2 = package1 << 8 | package2

            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digT3_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digT3_LSB)
            dig_T3 = package1 << 8 | package2

            # bosch api .c-ből koppintva
            var1 = ((((adc_T>>3) - (dig_T1<<1))) * (dig_T2)) >> 11
            var2 = (((((adc_T>>4) - (dig_T1)) * ((adc_T>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
            t_fine = var1 + var2
            T = (t_fine * 5 + 128) >> 8
            return T

class Sensor_DHT11:
    PIN = 7 
    SAMPLE_TIME = 10 / 1000 / 1000

    def __init__(self):
        pass

    def read(self):
        pass


class SensorHandler:
    def __init__(self):
        #self.dht11Device = adafruit_dht.DHT11(board.D4)
        self.bm280Device = Sensor_BM280()

    def read(self):
        try:
            #temperature1 = self.dhtDevice.temperature
            #humidity1 = self.dhtDevice.humidity
            self.bm280Device.triggerMeasurement()
            temperatureBM280 = self.bm280Device.getTemperature()
            return [10, 20, 11, temperatureBM280, 110000]
        except RuntimeError as error:
            print(error.args[0])
            return None, None