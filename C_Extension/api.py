import subprocess


PROGRAM_PATH = "./start_comm"

def readSensor():
    result = subprocess.run([PROGRAM_PATH], capture_output=True, text=True)
    with open("measurement.txt", "r") as f:
        data = f.read()
    data = data.replace("\n", "")
    message = ""
    #print(data)
    for i in data.split("10"):
        if "111" in i:
            message += "1"
        elif "111111111111" in i:
            pass
        else:
            message += "0"

    #print(message)
    humidity = bin(eval("0b"+message[-41:-33]))
    humidityDec = bin(eval("0b"+message[-33:-25]))
    temperature = bin(eval("0b"+message[-25:-17]))
    temperatureDec = bin(eval("0b"+message[-17:-9]))
    parity = bin(eval("0b"+message[-9:-1]))


    print(humidity)
    print(humidityDec)
    print(temperature)
    print(temperatureDec)
    print(parity)
    parity_calc = humidity + humidityDec + temperature + temperatureDec
    print(parity_calc)

readSensor()
