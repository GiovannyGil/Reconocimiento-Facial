import cv2
import numpy as np
import face_recognition as fr
import sqlite3
from datetime import datetime
import os.path
import time
# import RPi.GPIO as GPIO
import Jetson.GPIO as GPIO

main_directory = os.path.dirname(os.path.abspath(__file__)) # obtener la ruta principal dinamicamente en cualquier sitio y S.O
media_directory = 'media/' # ruta para ir a la media => ubicacion de las fotos
database_directory = 'ReconocimientoF.db' # ruta de la base de datos

conn = sqlite3.connect(os.path.join(main_directory, database_directory)) # ruta dinamica de la base de datos
cursor = conn.cursor() # ruta dinamica de la base de datos
cursor.execute('SELECT nombres, apellidos, foto FROM usuarios_persona') # Consulta SQL para obtener datos de los usuarios
users_data = cursor.fetchall() # extraer los datos de la consulta


x1, y1, x2, y2 = 0, 0, 0, 0 # coordenadas iniciales
color_verde = (0, 255, 0) # B, G, R para verde
color_rojo = (0, 0, 255) # B, G, R para rojo
ultima_hora_registro = None # variable de tiempo

def registrar_registro(usuario_id): # funcion para registrar el registro(fecha y hora del reconocimiento)
    global ultima_hora_registro # instanciar variable global de hora
    hora_actual = datetime.now() # optener la fecha y hora del sistema
    hora_entrada = hora_actual.strftime('%Y-%m-%d %H:%M:%S') # entregar la fecha y hora

    if ultima_hora_registro is None or (hora_actual - ultima_hora_registro).total_seconds() >= 10: # Verificar si ha pasado al menos 10 segundos desde el último registro
        cursor.execute("INSERT INTO usuarios_registros (UsuarioID_id, fecha) VALUES (?, ?)", (usuario_id, hora_entrada)) # Insertar el registro en la tabla Registros
        conn.commit() # guardar cambios
        ultima_hora_registro = hora_actual # comparar horas (verificar si genera otro registro o no)


def cargar_usuarios(): # funcion para cargar los usuarios
    cursor.execute('SELECT nombres, apellidos, foto FROM usuarios_persona') # extraer los datos de la consulta
    return cursor.fetchall() # retornar los datos

def detectar_rostros(frame): # funcion para detectar rostros
    frame2 = cv2.resize(frame, (0, 0), None, 0.25, 0.25) # redimensionar el frame
    rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB) # convertir el frame a RGB
    faces = fr.face_locations(rgb) # instanciar el rostro con el nuevo color
    facesCod = fr.face_encodings(rgb, faces) # codificar el rostro
    return faces, facesCod # retornar el rostro y la codificacion

def dibujar_recuadro(frame, faceloc, color, text=''): # funcion para dibujar el recuadro
    y1, x2, y2, x1 = faceloc # extraer las coordenadas
    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4 # multiplicar las coordenadas por 4
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2) # dibujar el recuadro de la parte superior
    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), color, cv2.FILLED) # dibujar el recuadro de la parte inferior
    cv2.putText(frame, text, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

def cargar_y_comparar_rostro(user_data, faceCod): # funcion para cargar y comparar el rostro
    nombre, apellido, foto_path = user_data # extraer la informacion del usuario
    known_image_path = os.path.join(main_directory, media_directory, foto_path) # complemento de la ruta raiz con la ruta de la foto
    known_image = fr.load_image_file(known_image_path) # cargar ruta de la foto
    known_face_encoding = fr.face_encodings(known_image)[0]  # codificar el rostro

    results = fr.compare_faces([known_face_encoding], faceCod) # comparar el rostro
    return results[0] # retornar el resultado

def pulso(Acceso):
    if Acceso == 1:
        print('Acceso Permitido ',Acceso)

        # enviar pulso 
        lista_pines = [7, 8, 9]
        try:
            # Configurar el modo del pin como salida
            GPIO.setmode(GPIO.BOARD)

            # Configurar todos los pines en la lista como salida
            for pin in lista_pines:
                GPIO.setup(pin, GPIO.OUT)

            # Enviar un pulso de 5V durante 5 segundos en cada pin
            for pin in lista_pines:
                GPIO.output(pin, GPIO.HIGH)
            
            time.sleep(10)  # Esperar 10 segundos
            
            # Apagar todos los pines al finalizar
            for pin in lista_pines:
                GPIO.output(pin, GPIO.LOW)
        finally:
            # Limpiar los pines GPIO al finalizar
            GPIO.cleanup()
    else:
        print('Acceso Denegado ', Acceso)

def procesar_resultado(match, frame, faceloc, color, nombre): # funcion para procesar el resultado
    if match: # si hay match
        dibujar_recuadro(frame, faceloc, color, nombre) # dibujar el recuadro
        print('Usuario reconocido: ', nombre)  # mostraer el nombre del usuario reconocido (en consola)
        Acceso = 1 # instanciar variable en 1
        pulso(Acceso)

        cursor.execute("SELECT ID FROM usuarios_persona WHERE nombres = ?", (nombre,)) # extraer el ID del usuario
        result = cursor.fetchone() # extraer el resultado
        if result: # si hay resultado
            usuario_id = result[0] # extraer el ID del usuario
            registrar_registro(usuario_id) # registrar el registro(fecha y hora del reconocimiento)


    else:
        dibujar_recuadro(frame, faceloc, color_rojo, 'Desconocido') # dibujar el recuadro en rojo y mostrar desconocido
        print('Usuario No Reconocido') # mostrar en consola que no se reconoce el usuario
        Acceso = 0 # instanciar variable en 0
        pulso(Acceso)
        
def reconocer_rostro(frame, users_data, facesCod, faces): # funcion para reconocer rostros
    global Acceso # instanciar variable global
    for faceCod, faceloc in zip(facesCod, faces): # extraer la informacion del rostro
        x1, y1, x2, y2 = faceloc # extraer las coordenadas
        x1 -= 20
        y1 -= 20
        x2 += 20
        y2 += 20

        match = False # instanciar variable en falso

        for user_data in users_data: # extraer la informacion del usuario
            match = cargar_y_comparar_rostro(user_data, faceCod) # cargar y comparar el rostro
            if match: # si hay match
                break # salir del bucle

        procesar_resultado(match, frame, faceloc, color_verde, user_data[0]) # procesar el resultado


def main(): # funcion principal
    cap = cv2.VideoCapture(0) # instanciar la camara
    while True: # bucle infinito
        ret, frame = cap.read() # leer la camara

        faces, facesCod = detectar_rostros(frame) # detectar rostros
        reconocer_rostro(frame, users_data, facesCod, faces) # reconocer rostros

        cv2.imshow('RECONOCIMIENTO FACIAL', frame) # titulo del frame

        t = cv2.waitKey(1) # tiempo de espera para cerrar la ventana
        if t == 27: # si se presiona la tecla ESC
            break # cerrar el bucle infinito

    conn.close() # cerrar la conexion con la BBDD
    cap.release() # cerrar la camara
    cv2.destroyAllWindows() # cerrar todas las ventanas 

if __name__ == "__main__": # funcion principal
    main() # ejecutar el programa
