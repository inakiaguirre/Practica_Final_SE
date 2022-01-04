import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import analog_light
import dht_config
import json
import time
import servomotor
import RPi.GPIO as GPIO
from grove.helper import SlotHelper


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


#_________________________________________________________________

# Definimos los pines de entrada de los dispositivos. 
pin_sensor = 16 
pin_luz = 5
pin_boton = 6
pin = 12
frecuencia = 50

sh = SlotHelper(SlotHelper.ADC)
pin = sh.argv2pin()
pin_lumi = analog_light.GroveLightSensor(pin)


GPIO.setup(pin_luz, GPIO.OUT)
GPIO.setup(pin_boton, GPIO.IN)

#_________________________________________________________________

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

#_________________________________________________________________

angulo = 0
luminosidad = 0



sensor = dht_config.DHT(pin_sensor) 
miservo = servomotor.SERVOMOTOR(pin, frecuencia)
mianaloglight = analog_light.GroveLightSensor(pin_lumi)

miservo.anguloInicial()

while True:

    humi, temp = sensor.read() 
    servo = miservo.movimiento()
    lumi = mianaloglight.main()

    # Creamos un diccionario con los valores que vamos a publicar
    mensaje = {
        
        "humi": humi,
        "temp": temp,
        "servo": servo,
        "lumi": lumi

    }

    # Convertimos los mensaje en tipo JSON
    mensaje_json_temp_humi = json.dumps(mensaje)

    # Publicamos todos los topics
    publish.multiple([[tp_temp_hum, mensaje_json_temp_humi], [tp_lumi, mensaje_json_temp_humi], [tp_servo, mensaje_json_temp_humi]], hostname=hostname)

    time.sleep(3)
