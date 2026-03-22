import subprocess


PROGRAM_PATH = "./start_comm"

def readSensor():
    result = subprocess.run([PROGRAM_PATH], capture_output=True, text=True)
    with open("measurement.txt", "r") as f:
        data = f.read()

    print(data)