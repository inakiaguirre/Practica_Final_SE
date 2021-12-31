import time,sys
import smbus
import RPi.GPIO as GPIO

# Seleccionar el bus I2C
bus = smbus.SMBus(1)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN)
GPIO.setup(5, GPIO.OUT, initial=1)

address = 0x04  
        
#LLamar una vez para inicializar el convertidor.
def init_adc():
	bus.write_byte(0x04, 0x30)

def adc_read():
	data=bus.read_word_data(0x04, 0x30)
	return data

while True:
    valor = adc_read()
    if valor < 510:
        print("Valor: " + str(valor))
        GPIO.output(5, GPIO.HIGH)
        print("Luz encendida")
    elif valor > 500:
        print("Valor: " + str(valor))
        GPIO.output(5, GPIO.LOW)
        print("Luz apagada")
    time.sleep(2)
