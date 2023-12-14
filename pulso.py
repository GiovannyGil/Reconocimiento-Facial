import Jetson.GPIO as GPIO
import time

# definir el pin
PIN = 7

try:
    # configurar el modo del pin como salida
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN, GPIO.OUT)

    # Enviar un pulso de 5V durante 5 segundos
    GPIO.output(PIN, GPIO.HIGH)
    time.sleep(15) # esperar 5 segundos
    GPIO.output(PIN, GPIO.LOW)
finally:
    # limpiar losp ines GPIO al finalizar
    GPIO.cleanup()
