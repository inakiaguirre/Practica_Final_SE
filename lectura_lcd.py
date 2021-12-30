import sys
import time
import  RPi.GPIO as GPIO
import smbus
import dht_config


#importar modulo del display LCD
import lcd

rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)


LCD_LINE_1 = 0x80 # DIRECCION RAM PARA PRIMERA LINEA
LCD_LINE_2 = 0xC0 # DIRECCION RAM PARA SEGUNDA LINEA
LCD_CMD = False
#------------------------------------------------------------------

# Direccion I2C del display
i2c_adress = 0x3e


# Establecemos los pines a usar, y los definimos como entrada o salida segun el sensor

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

pin_buzzer = 26

#------------------------------------------------------------------




def tempHum():
     
    GPIO.setmode(GPIO.BCM)

    gpio_pin_sensor = 16 
    sensor = dht_config.DHT(gpio_pin_sensor) 
    
    while True:
        humi, temp = sensor.read()
        print('Humedad {0:.1f}%, Temperatura {1:.1f}'.format( humi, temp))
   
        time.sleep(1)
    
        return temp, humi

tempHum()

def mostrarPantalla():
    pantalla = lcd.LCD_DISPLAY(i2c_adress)
    datos = tempHum()
    pantalla.setText(datos)
    comprobarTemp(datos)

def comprobarTemp(temp):

    global pin_buzzer
    GPIO.setup(pin_buzzer, GPIO.OUT)
    
    if temp > 22:
        print("Temperatura Correcta " + str(temp) + " C")
    elif 25 < temp < 30:
        print("Temperatura Alta " + str(temp) + " C")
        GPIO.output(pin_buzzer, True)
        time.sleep(0.5)
        GPIO.output(pin_buzzer, False)



mostrarPantalla()