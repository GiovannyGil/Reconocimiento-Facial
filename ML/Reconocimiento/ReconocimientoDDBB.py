# Dependencias
import cv2
import numpy as np
import face_recognition as fr
import os
from datetime import datetime
import random
import sqlite3

# crear conexion a la base de datos
conn = sqlite3.connect('reconocimiento.db')


# Crear un objeto cursor para ejecutar comandos SQL
cursor = conn.cursor()


# Acceso a la carpeta
path = '/home/jorge/Documentos/Sistema-Reconocimiento-Facial-Instalaciones/ML//fotos/'
images = []  # Lista de imágenes
clases = []  # Lista de nombres
lista = os.listdir(path)  # Lista de archivos en la carpeta
comp1 = 100  # Umbral de comparación
# Declaración de color verde
color_verde = (0, 255, 0)  # R, G, B para verde
# Declaración de color rojo
color_rojo = (0, 0, 255)  # R, G, B para rojo
print(lista)

for lis in lista:
    # leer las imágenes de los rostros
    imgdb = cv2.imread(f'{path}/{lis}')  # Leer la imagen
    # almacenar las imágenes en una lista
    images.append(imgdb)
    # almacenar el nombre de la imagen en una lista
    clases.append(os.path.splitext(lis)[0])  # almacenar el nombre de la imagen sin la extensión
print(clases)

# Función para codificar las imágenes
def codRostros(images):
    listCod = []

    # iterar las imágenes
    for img in images:
        # convertir a escala de grises
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # codificar la imagen
        cod = fr.face_encodings(img)[0]
        # almacenar la codificación en una lista
        listCod.append(cod)
    return listCod

# Abrir el archivo en modo lectura y escritura -> archivo csv donde se guarda el registro de hora de entrada y salida
import time  # Importa el módulo time
# Declaración de variables globales
ultima_entrada = None  # Variable para registrar la hora de la última entrada
# Función para registrar la hora
def horario(nombre):
    global ultima_entrada  # Declarar la variable global
    with open('Horario.csv', 'a') as h:  # 'a' para abrir en modo append (agregar al archivo)
        info = datetime.now()  # obtener la hora actual
        # extraer la fecha
        fecha = info.strftime('%Y:%m:%d')
        # extraer la hora
        hora = info.strftime('%H:%M:%S')

        # Verificar si ha pasado suficiente tiempo desde la última entrada
        if ultima_entrada is None or (info - ultima_entrada).total_seconds() > 60:  # Por ejemplo, 60 segundos de espera
            # guardar la información en el archivo
            h.writelines(f'\n{nombre},{fecha},{hora},Entrada')
            print(info)
            ultima_entrada = info  # Actualiza la hora de la última entrada

# Llamar la función para codificar las imágenes
rostrosCOD = codRostros(images)

# Llamar la cámara
cap = cv2.VideoCapture(0)
horas_entrada = {}  # Diccionario para rastrear la hora de entrada de cada persona
# Fuera del bucle, antes de comenzar a capturar imágenes
horas_entrada_desconocido = {}  # Diccionario para rastrear la hora de entrada de rostros desconocidos
# Tiempo mínimo entre registros para la misma persona (en segundos)
tiempo_minimo_registro = 15
# Definir coordenadas iniciales
x1, y1, x2, y2 = 0, 0, 0, 0

while True:
    # Leer los frames de la cámara
    ret, frame = cap.read()
    # Redimensionar las imágenes
    frame2 = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    # Convertir a escala de grises
    rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
    # Buscar los rostros en la imagen
    faces = fr.face_locations(rgb)
    facesCod = fr.face_encodings(rgb, faces)
    # Obtener la hora actual
    hora_actual = datetime.now()

    # Iterar los rostros
    for faceCod, faceloc in zip(facesCod, faces):
        # Comparar los rostros de la DDBB con la cámara
        comparacion = fr.compare_faces(rostrosCOD, faceCod)
        # Calcular la coincidencia de imagen cámara
        simi = fr.face_distance(rostrosCOD, faceCod)
        # Buscar el valor más bajo -> mayor coincidencia
        min = np.argmin(simi)
        # Aumentar el tamaño del rectángulo
        x1, y1, x2, y2 = faceloc  # Obtener las coordenadas originales
        # x = max(x1 - 10, 0)  # Calcular nuevas coordenadas
        # y = max(y1 - 10, 0)
        # w = x2 - x1 + 20
        # h = y2 - y1 + 20
        x1 -= 10
        y1 -= 10
        x2 += 20
        y2 += 20
        
        if comparacion[min]:
            # Comparar la coincidencia con el umbral
            nombre = clases[min]  # Obtener el nombre de la persona
            print(nombre)
            # Obtener las coordenadas
            y1, x2, y2, x1 = faceloc
            # Redimensionar las coordenadas
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            # Establecer el color verde
            r, g, b = color_verde
            # Cambiar el color de la caja a verde
            cv2.rectangle(frame, (x1, y1), (x2, y2), (r, g, b), 3)  # Rectángulo para el rostro
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (r, g, b), cv2.FILLED)  # Rectángulo para el nombre
            cv2.putText(frame, nombre, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)  # Texto para el nombre

            # Verificar si ha pasado suficiente tiempo desde la última entrada para la misma persona
            if nombre not in horas_entrada or (hora_actual - horas_entrada[nombre]).total_seconds() >= tiempo_minimo_registro:
                # Registrar la hora de entrada
                hora_entrada = hora_actual.strftime('%Y:%m:%d,%H:%M:%S')
                horas_entrada[nombre] = hora_actual
                print(f'{nombre} - Hora de entrada registrada')
                with open('Horario.csv', 'a') as h:
                    h.writelines(f'{nombre},{hora_entrada},Entrada\n')
        else:
            # Si no se detecta un rostro conocido, pintar un cuadro rojo con "desconocido"
            # Obtener las coordenadas
            y1, x2, y2, x1 = faceloc
            # Redimensionar las coordenadas
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            r, g, b = color_rojo
            cv2.rectangle(frame, (x1, y1), (x2, y2), (r, g, b), 3)  # Rectángulo para el rostro
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (r, g, b), cv2.FILLED)  # Rectángulo para "desconocido"
            cv2.putText(frame, "Desconocido", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)  # Texto para "desconocido"

    # Mostrar Frame
    cv2.imshow('RECONOCIMIENTO FACIAL', frame)

    # Leer el teclado
    t = cv2.waitKey(1)
    if t == 27:
        break

# Liberar la cámara y cerrar la ventana
cap.release()
cv2.destroyAllWindows()

# Guardar los cambios en la base de datos
conn.commit()

# Cerrar la conexión cuando hayas terminado
conn.close()