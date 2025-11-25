import serial
import time

SOGLIA_CADUTA = 60

def manda(mess):
    rasp_serial.write(mess)
    if (rasp_serial.in_waiting > 0):
        print("MVD dice", rasp_serial.readline().decode().strip())
def prendi_max():
    rasp_serial.write(b'MSV?3,1(x)')
    val_max = int(rasp_serial.readline().decode().strip())
    return val_max

massimi = []
max_n = 0
max_v = 0
flag_max = False
rasp_serial = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)
count = 0

manda(bytes([18]))
time.sleep(2)
manda(b"BDR6,2,1(x)")
time.sleep(1)
manda(b"ADR0(x)")
time.sleep(1)
manda(b"COF0(x)")
time.sleep(1)

while(True):
    max_v = max_n
    max_n = prendi_max()

    if max_n < max_v:
        flag_max = False
    if max_n > SOGLIA_CADUTA:
        if max_n == max_v:
            count += 1
        if max_n != max_v:
            count = 0
    if count > 2 and flag_max == False:
        massimi.append(max_n)
        flag_max = True


