import time
import  RPi.GPIO as GPIO
import smbus
import Adafruit_DHT
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
     
    sensor = Adafruit_DHT.DHT11 #Cambia por DHT22 y si usas dicho sensor
    pin = 16 #Pin en la raspberry donde conectamos el sensor
    humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin)

    print ('Humedad: ' , humedad)
    print ('Temperatura: ' , temperatura)
    
    
    return temperatura
    

def mostrarPantalla():
    pantalla = lcd.LCD_DISPLAY(i2c_adress)
    datos = tempHum()
    pantalla.setText("Temp: " + str(datos))
    comprobarTemp(datos)

def comprobarTemp(temp):

    global pin_buzzer
    GPIO.setup(pin_buzzer, GPIO.OUT)
    
    if 15 < temp < 25:
        print("Temperatura Correcta " + str(temp) + " C")
        
    elif temp > 25:

        print("Temperatura Alta " + str(temp) + " C")
        print('Buzzer ON')

        GPIO.output(pin_buzzer, True)
        time.sleep(0.5)
        GPIO.output(pin_buzzer, False)

    elif temp < 15:
        print("Temperatura baja " + str(temp) + " C")

        print('Buzzer ON')
        GPIO.output(pin_buzzer, True)
        time.sleep(0.5)
        GPIO.output(pin_buzzer, False)


while True:
    mostrarPantalla()