import time
import  RPi.GPIO as GPIO
import smbus
import Adafruit_DHT
import lcd
import time
from grove.adc import ADC
import RPi.GPIO as GPIO
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN)
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 50) 
GPIO.setup(5, GPIO.OUT, initial=1)



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


#________________________________________________________________________________________________

# SENSOR TEMP-HUM Y LCD

def tempHum():
     
    sensor = Adafruit_DHT.DHT11 #Cambia por DHT22 y si usas dicho sensor
    pin = 16 #Pin en la raspberry donde conectamos el sensor
    humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin)
    print("SENSOR TEMPERATURA - HUMEDAD:")
    print ('Humedad: ' , humedad)
    print ('Temperatura: ' , temperatura)
    
    
    return temperatura, humedad
    

def mostrarPantalla():
    pantalla = lcd.LCD_DISPLAY(i2c_adress)
    temperatura, humedad = tempHum()
    pantalla.setText("Temp: " + str(temperatura))
    comprobarTemp(temperatura)
    print()


def comprobarTemp(temp):

    global pin_buzzer
    GPIO.setup(pin_buzzer, GPIO.OUT)
    
    if 15 < temp <= 25:
        print("Temperatura Correcta " + str(temp) + " C")
        GPIO.output(pin_buzzer, False)
        pwm.ChangeDutyCycle(2.5)
        print("ESTADO DEL TECHO:")
        print("Techo cerrado")
        print()

        return "Techo Cerrado"
        
    elif temp > 25:

        print("Temperatura Alta " + str(temp) + " C")
        print('Buzzer ON')
        pwm.ChangeDutyCycle(12.5)
        print("ESTADO DEL TECHO:")
        print("Techo abierto")
        print()

        GPIO.output(pin_buzzer, True)
        time.sleep(0.5)
        GPIO.output(pin_buzzer, False)

        return "Techo Abierto"

    elif temp < 15:
        print("Temperatura baja " + str(temp) + " C")
        pwm.ChangeDutyCycle(2.5)

        print('Buzzer ON')
        GPIO.output(pin_buzzer, True)
        time.sleep(0.5)
        GPIO.output(pin_buzzer, False)

        print("ESTADO DEL TECHO:")
        print("Techo cerrado")
        print()

        return "Techo Cerrado"


#________________________________________________________________________________________________

# SERVOMOTOR

masMenos = True

#Inicializacion angulo a 0 grados
angulo = 0

#FunciÃ³n para calcular el Ã¡ngulo
def angle_to_percent (angle):
    if angle > 180 or angle < 0:
        return False

    start = 2.5
    end = 12.5
    ratio = (end - start)/180 #Calcular el porcentaje de ratio

    angle_as_percent = angle * ratio

    return start + angle_as_percent

#Mover el servomotor a 0 grados siempre que empieze desde el prinicpio
pwm.start(angle_to_percent(0)) 

#Funcion que suma de 10 en 10 hasta 180 y despues resta de 10 en 10 hasta 0 cada vez que pulsamos
def movimiento(n):
    
    global angulo
    global masMenos
    
    if masMenos == True:
        angulo += 180
        masMenos = False if angulo >= 180 else True
    else:
        angulo -= 180
        masMenos = True if angulo <= 0 else False
        
    pwm.ChangeDutyCycle(angle_to_percent(angulo))

    if angulo == 180:
        print("ESTADO DEL TECHO:")
        print("Techo abierto - Manual")
    else:
        print("ESTADO DEL TECHO:")
        print("Techo cerrado - Manual")

    print("El angulo actual es: " + str(angulo))
    print()

    return angulo

GPIO.add_event_detect(6, GPIO.RISING, callback = movimiento, bouncetime = 200)

#________________________________________________________________________________________________

# SENSOR LUMINOSIDAD

__all__ = ["GroveLightSensor"]

class GroveLightSensor(object):

    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def light(self):
        value = self.adc.read(self.channel)
        return value

Grove = GroveLightSensor


def main():
    print("SENSOR DE LUMINOSIDAD:")
    from grove.helper import SlotHelper
    sh = SlotHelper(SlotHelper.ADC)
    pin = sh.argv2pin()

    estadoLuz = ""

    sensor = GroveLightSensor(pin)

    print('Detectando luz...')

    while True:
        print('Valor de luminosidad en el ambiente: {0}'.format(sensor.light))
        if sensor.light < 600:
            GPIO.output(5, GPIO.HIGH)
            print("Luz encendida")
            print()
            estadoLuz = "Luz encendida"
        elif sensor.light >= 600:
            GPIO.output(5, GPIO.LOW)
            print("Luz apagada")
            print()

            estadoLuz = "Luz Apagada"
        
        time.sleep(2)
    
        return sensor.light, estadoLuz

#________________________________________________________________________________________________

# PUBLICADOR

# Direccion del broker.
hostname = 'localhost'

#_________________________________________________________________

# Definimos los topics para MQTT
# Topics que publicamos.
tp_temp_hum = "t_temp_hum"
tp_lumi = "t_lumi"
tp_servo = "t_servo"
tp_luz = "t_luz"

#_________________________________________________________________

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def on_message(client, userdata, message):
    
    rec_values = message.payload.decode("utf-8")
    rec_values_json = json.loads(rec_values)

#_________________________________________________________________

# Creamos un cliente MQTT
client = mqtt.Client()

# Definimos los callbacks para conectarnos y subscribirnos al topic
client.on_connect = on_connect
client.on_message = on_message

# Conectamos al hosntame que se debe definir arriva
client.connect(hostname, 1883, 60)

# Inicialmos el loop de la siguiente manera:
client.loop_start()


if __name__ == '__main__':



    while True:

        mostrarPantalla()

        temp, humi = tempHum()
        servo = comprobarTemp(temp)
        lumi, estadoLuz = main()

        # Creamos un diccionario con los valores que vamos a publicar
        mensaje = {
            
            "humi": humi,
            "temp": temp,
            "servo": servo,
            "lumi": lumi,
            "estadoLuz": estadoLuz

        }

        # Convertimos los mensaje en tipo JSON
        mensaje_json = json.dumps(mensaje)

        # Publicamos todos los topics
        publish.multiple([[tp_temp_hum, mensaje_json], [tp_lumi, mensaje_json], [tp_servo, mensaje_json]], hostname=hostname)
        time.sleep(2)
