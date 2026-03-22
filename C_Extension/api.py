import subprocess


PROGRAM_PATH = "./start_comm"

def readSensor():
    result = subprocess.run([PROGRAM_PATH], capture_output=True, text=True)
    with open("measurement.txt", "r") as f:
        data = f.read()
    data = data.replace("\n", "")
    message = ""
    print(data)
    for i in data.split("10"):
        if "111" in i:
            message += "1"
            print(1)
        elif "111111111111" in i:
            pass
        else:
            message += "0"
            print(0)

    print(message[-40:-32])
    print(message[-32:-24])
    print(message[-24:-16])
    print(message[-16:-8])
    print(message[-8:])

readSensor()
