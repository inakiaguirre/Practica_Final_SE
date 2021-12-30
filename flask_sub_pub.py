# --------------------------------------------------------------
#    SERVICIO WEB CON FLASK + MQTT + SOCKET-IO
#    
#    Ejemplo para realizar para Laboratorio 3. Parte 2

# Ejemplo de uso de librerías flask_mqtt y  flask_socketio
# --------------------------------------------------------------
#   @Laura Arjona
#  @Sistemas Embebidos. 2021
# -----------------------------------


import json
import time
import subprocess 
import random
import os
import time
import RPi.GPIO as GPIO
import dht_config
import RPi.GPIO as GPIO
from time import sleep

import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

import json
import time
import subprocess 
import random
import os
import time


#Direccion del broker
#El hostname es la direccion IP del broker
#Si el broker esta en la misma maquina que ejecuta este scritp, 
#se puede usar local host como IP. Recordad localhost = 127.0.0.1
hostname = 'localhost'

#_________________________________________________________________________________

#Definimos los topics para MQTT
#Topics Subscriptor
topic_pub1 = "dht11/m1"
topic_pub2 = "mState/m1"
topic_pub3 = "cpu_temp/m1"

#Topic Publicador
topic_sub1 = "mAction/m1"

#_________________________________________________________________________________

# Establezco los pines a los que está conectado el pulsador LED
led = 5
boton = 6
sensor = dht_config.DHT(16)
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
GPIO.setup(led, GPIO.OUT, initial=1)

#_________________________________________________________________________________

# Callback que se llama cuando el cliente recibe el CONNACK del servidor 
#Restult code 0 significa conexion sin errores
def on_connect(client, userdata, flags, rc):

    print("Connected with result code "+str(rc))
 
    # Nos subscribirmos al topic 
    client.subscribe(topic_sub1)
    client.subscribe("mAction/m1")
    
    

#_________________________________________________________________________________

# Callback que se llama "automaticamente" cuando se recibe un mensaje del Publiser.
def on_message(client, userdata, message):
    print("MENSAJE RECIBIDO DESDE SERVIDOR")
    message.payload = message.payload.decode("utf-8")
    
    print("topic:  "+ message.topic)
    
    msg_rec =message.payload 
    
    if message.topic ==topic_sub1:
        print(msg_rec)

        if msg_rec == '{"action": "encender"}':
            print("Encender LED")
            GPIO.output(led, GPIO.HIGH)
            #Encender máquina => encender LED
        else: 
            print("Apagar LED")
            GPIO.output(led, GPIO.LOW)
            #Apagar máquina => apagar LED

os.system("vcgencmd measure_temp")
   
#_________________________________________________________________________________  

 # Creamos un cliente MQTT 
client = mqtt.Client()
#Definimos los callbacks para conectarnos y subscribirnos al topic
client.on_connect = on_connect
client.on_message = on_message
#Conectamos al hosntame que se debe definir arriva
client.connect(hostname, 1883, 60)
#En vez de iniciar el bucle infinito como hicimos en la actividad de clase
# inicialmos el loop de la siguiente manera:
client.loop_start() 


while True:

# Topic 1
    GPIO.setmode(GPIO.BCM) #numeración de pines basada en números GPIOs
    gpio_pin_sensor = 16 #GPIO 16   conectamos el pin SIG del sensor
    sensor = dht_config.DHT(gpio_pin_sensor) #Pasar por argumento el número del GPIO

    temp1 = os.popen("vcgencmd measure_temp").readline()
    temp1 = temp1.replace("temp=", "")
    temp1 = temp1.replace("'C", "")

    print("Temperatura CPU: " + temp1 )

    humi, temp = sensor.read()    

    estado = 0

    h = humi/100

    print('Humedad {0:.1f}%, Temperatura {1:.1f}'.format( humi, temp))


    mensaje1= {
    "humi": humi,
    "temp": temp,
    }

    #Convertimos el mensaje en tipo JSON
    mensaje1_json= json.dumps(mensaje1)
    #Publicamos los valores por MQTT, para que los reciva el servidor FLASK
    publish.single(topic_pub1, mensaje1_json, hostname=hostname)

#--------------------------------------------------------------------------

# Topic 2
    mensaje2= {
    "estado": estado
    }
    #Convertimos el mensaje en tipo JSON
    mensaje2_json= json.dumps(mensaje2)
    #Publicamos los valores por MQTT, para que los reciva el servidor FLASK
    publish.single(topic_pub2, mensaje2_json, hostname=hostname)

#--------------------------------------------------------------------------

# Topic 3
    
    mensaje3= {
        "temp1": temp1
    }

    #Convertimos el mensaje en tipo JSON
    mensaje3_json= json.dumps(mensaje3)
    #Publicamos los valores por MQTT, para que los reciva el servidor FLASK
    publish.single(topic_pub3, mensaje3_json, hostname=hostname)

    time.sleep(3)

