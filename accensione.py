import serial
import time
import subprocess

#from funzioni import *

rasp_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(1)

def lancia_script(path):
    result = subprocess.run(
        ["python3", path],
        capture_output=True,
        text=True
    )

    return result.returncode

def manda(mess):
    rasp_serial.write(mess)
    if (rasp_serial.in_waiting > 0):
        print("MVD dice", rasp_serial.readline().decode().strip())


manda(bytes([18]))
time.sleep(2)
manda(b"BDR6,2,1(x)")
time.sleep(1)
manda(b"ADR0(x)")
time.sleep(1)
manda(b"COF0(x)")
time.sleep(1)


