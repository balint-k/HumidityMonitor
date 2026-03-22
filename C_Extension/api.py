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
    humidity = message[-41:-33]
    humidityDec = message[-33:-25]
    temperature = message[-25:-17]
    temperatureDec = message[-17:-9]
    parity = message[-9:-1]

    parity_calcualted = ""
    count = 0
    for i in range(1,9):
        for data in [humidity,humidityDec,temperature,temperatureDec]:
            if data[-i] == "1":
                count += 1
        if count % 2 == 1:
            parity_calcualted = "1" + parity_calcualted 
        else:
            parity_calcualted = "0" + parity_calcualted 
        count = int((count - count % 2) / 2) # kovi

    print(parity_calcualted == parity)
    print(int(bin(eval("0b"+ humidity))))
    print(int(bin(eval("0b"+ temperature))))
    
readSensor()
