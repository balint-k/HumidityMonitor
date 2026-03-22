import time
import smbus

from C_Extension import getData

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

    REGISTER_digP1_MSB = 0x8F
    REGISTER_digP1_LSB = 0x8E
    REGISTER_digP2_MSB = 0x91
    REGISTER_digP2_LSB = 0x90
    REGISTER_digP3_MSB = 0x93
    REGISTER_digP3_LSB = 0x92
    REGISTER_digP4_MSB = 0x95
    REGISTER_digP4_LSB = 0x94
    REGISTER_digP5_MSB = 0x97
    REGISTER_digP5_LSB = 0x96
    REGISTER_digP6_MSB = 0x99
    REGISTER_digP6_LSB = 0x98
    REGISTER_digP7_MSB = 0x9B
    REGISTER_digP7_LSB = 0x9A
    REGISTER_digP8_MSB = 0x9D
    REGISTER_digP8_LSB = 0x9C
    REGISTER_digP9_MSB = 0x9F
    REGISTER_digP9_LSB = 0x9E

    REGISTER_digH1 = 0xA1
    REGISTER_digH2_MSB = 0xE2
    REGISTER_digH2_LSB = 0xE1
    REGISTER_digH3 = 0xE3
    REGISTER_digH4_MSB = 0xE4
    REGISTER_digH4_LSB_3_0 = 0xE5
    REGISTER_digH5_MSB = 0xE6
    REGISTER_digH5_LSB_7_4 = 0xE5
    REGISTER_digH6 = 0xE7



    def __init__(self):
        self.available = self.verifySensor()
        if self.available:
            self.enableTemperatureMeasurement()
            self.enablePressureMeasurement()
            self.enableHumidityMeasurement()

    def exit(self):
        self.available = self.verifySensor()
        if self.available:
            self.disableTemperatureMeasurement()
            self.disablePressureMeasurement()
            self.disableHumidityMeasurement()

        
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

    def getTemperature(self, get_t_fine = False):
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

        # bosch api .c-ből koppintva a kompenzalas
        var1 = ((((adc_T>>3) - (dig_T1<<1))) * (dig_T2)) >> 11
        var2 = (((((adc_T>>4) - (dig_T1)) * ((adc_T>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
        t_fine = var1 + var2

        if get_t_fine:
            return t_fine # nyomashoz

        T = (t_fine * 5 + 128) >> 8
        return T /100
        # bosch datasheet: // Returns temperature in DegC, resolution is 0.01 DegC. Output value of “5123” equals 51.23 DegC.
        # itt van float

    def enablePressureMeasurement(self):
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            message = registryContent | 0b00001000 # 010 oversampling x2
            bus.write_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS, message)
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            masked = registryContent & 0b00001000
            if masked == 0:
                raise ValueError("Pressure measurement can\'t be enabled")

    def disablePressureMeasurement(self):
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            message = registryContent & 0b11100011 
            bus.write_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS, message)
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_MEAS)
            masked = registryContent & 0b00011100
            if masked != 0:
                raise ValueError("Pressure measurement can\'t be disabled")

    def getPressure(self):
        with SMBus() as bus:
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_PRESS_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_PRESS_LSB)
            package3 = bus.read_byte_data(self.ADDRESS, self.REGISTER_PRESS_XLSB)

            adc_P = package1 << 12 | package2 << 4 | package3 >> 4

            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP1_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP1_LSB)
            dig_P1 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP2_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP2_LSB)
            dig_P2 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP3_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP3_LSB)
            dig_P3 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP4_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP4_LSB)
            dig_P4 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP5_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP5_LSB)
            dig_P5 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP6_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP6_LSB)
            dig_P6 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP7_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP7_LSB)
            dig_P7 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP8_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP8_LSB)
            dig_P8 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP9_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digP9_LSB)
            dig_P9 = package1 << 8 | package2

        t_fine = self.getTemperature(get_t_fine = True)
        # datasheetbol kiszedett kompenzaci
        var1 = (t_fine) - 128000
        var2 = var1 * var1 * dig_P6
        var2 = var2 + ((var1* dig_P5)<<17)
        var2 = var2 + ((dig_P4)<<35)
        var1 = ((var1 * var1 * dig_P3)>>8) + ((var1 * dig_P2)<<12)
        var1 = ((((1)<<47)+var1))*(dig_P1)>>33
        if (var1 == 0):
            return 0 #// avoid exception caused by division by zero
        p = 1048576-adc_P
        p = int((((p<<31)-var2)*3125)/var1)
        var1 = ((dig_P9) * (p>>13) * (p>>13)) >> 25
        var2 = ((dig_P8) * p) >> 19
        p = ((p + var1 + var2) >> 8) + ((dig_P7)<<4)
        return p / 256 / 1000 # kPa
        #// Output value of “24674867” represents 24674867/256 = 96386.2 Pa = 963.862 hPa

    def enableHumidityMeasurement(self):
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_HUM)
            message = registryContent | 0b00000010 # 010 oversampling x2
            bus.write_byte_data(self.ADDRESS, self.REGISTER_CTRL_HUM, message)
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_HUM)
            masked = registryContent & 0b00000010
            if masked == 0:
                raise ValueError("Humidity measurement can\'t be enabled")

    def disableHumidityMeasurement(self):
        with SMBus() as bus:
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_HUM)
            message = registryContent & 0b11111000 
            bus.write_byte_data(self.ADDRESS, self.REGISTER_CTRL_HUM, message)
            registryContent = bus.read_byte_data(self.ADDRESS, self.REGISTER_CTRL_HUM)
            masked = registryContent & 0b00000111
            if masked != 0:
                raise ValueError("Humidity measurement can\'t be disabled")

    def getHumidity(self):
        with SMBus() as bus:
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_HUM_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_HUM_LSB)

            adc_H = package1 << 8 | package2

            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH1)
            dig_H1 = package1
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH2_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH2_LSB)
            dig_H2 = package1 << 8 | package2
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH3)
            dig_H3 = package1
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH3)
            dig_H3 = package1
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH4_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH4_LSB_3_0)
            dig_H4 = package1 << 4 | (package2 & 0b00001111)
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH5_MSB)
            package2 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH5_LSB_7_4)
            dig_H5 = package1 << 4 | (package2 >> 4)
            package1 = bus.read_byte_data(self.ADDRESS, self.REGISTER_digH6)
            dig_H6 = package1

        t_fine = self.getTemperature(get_t_fine = True)
        v_x1_u32r = (t_fine - (76800))
        v_x1_u32r = (((((adc_H << 14) - ((dig_H4) << 20) - ((dig_H5) * v_x1_u32r)) +
        (16384)) >> 15) * (((((((v_x1_u32r * (dig_H6)) >> 10) * (((v_x1_u32r *
        (dig_H3)) >> 11) + (32768))) >> 10) + (2097152)) *
        (dig_H2) + 8192) >> 14));
        v_x1_u32r = (v_x1_u32r - (((((v_x1_u32r >> 15) * (v_x1_u32r >> 15)) >> 7) * (dig_H1)) >> 4))
        #v_x1_u32r = (v_x1_u32r < 0 ? 0 : v_x1_u32r)
        #v_x1_u32r = (v_x1_u32r > 419430400 ? 419430400 : v_x1_u32r)
        if v_x1_u32r < 0:
            v_x1_u32r = 0
        if v_x1_u32r > 419430400:
            v_x1_u32r = 419430400
        return (v_x1_u32r>>12) / 1024
        # // Output value of “47445” represents 47445/1024 = 46.333 %RH

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
            temperatureDHT11 , humidityDHT11 = getData()
            self.bm280Device.triggerMeasurement()
            temperatureBM280 = self.bm280Device.getTemperature()
            pressureBM280 = self.bm280Device.getPressure()
            humidityBM280 = self.bm280Device.getHumidity()
            return [humidityDHT11, temperatureDHT11, humidityBM280, temperatureBM280, pressureBM280]
        except RuntimeError as error:
            print(error.args[0])
            return None, None