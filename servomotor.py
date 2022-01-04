import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN)
GPIO.setup(12, GPIO.OUT)



masMenos = True

#Inicializacion angulo a 0 grados
angulo = 0


class SERVOMOTOR():

    def __init__(self, pin, frecuencia):
        self.pin = pin
        self.frecuencia = frecuencia

        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, self.frecuencia)

    #Funcion para calcular el angulo
    def angle_to_percent (self, angle = False):
        if angle > 180 or angle < 0:
            return False

        start = 2
        end = 10.5
        ratio = (end - start)/180 #Calcular el porcentaje de ratio

        angle_as_percent = angle * ratio

        return start + angle_as_percent

    #Mover el servomotor a 0 grados siempre que empieze desde el prinicpio
    def anguloInicial(self):

        self.pwm.start(self.angle_to_percent(0)) 

    #Funcion que suma de 10 en 10 hasta 180 y despues resta de 10 en 10 hasta 0 cada vez que pulsamos
    def movimiento(self, n = False):
        
        global angulo
        global masMenos
        
        if masMenos == True:
            angulo += 180
            masMenos = False if angulo >= 180 else True
        else:
            angulo -= 180
            masMenos = True if angulo <= 0 else False
            
        self.pwm.ChangeDutyCycle(SERVOMOTOR.angle_to_percent(angulo))

        if angulo == 180:
            print("Techo abierto")
        else:
            print("Techo cerrado")

        print("El angulo actual es: " + str(angulo))

        return angulo

