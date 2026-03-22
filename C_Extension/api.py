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
        elif "111111111111" in i:
            pass
        else:
            message += "0"

    print(message)
    print(message[-41:-33])
    print(message[-33:-25])
    print(message[-25:-17])
    print(message[-17:-9])
    print(message[-9:])

readSensor()
