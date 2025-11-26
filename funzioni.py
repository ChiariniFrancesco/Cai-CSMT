import serial
import time

def manda(mess):
    rasp_serial.write(mess)
    if (rasp_serial.in_waiting > 0):
        print("MVD dice", rasp_serial.readline().decode().strip())
def prendi_max():
    rasp_serial.write(b'MSV?3,1(x)')
    val_max = int(rasp_serial.readline().decode().strip())
    return val_max
