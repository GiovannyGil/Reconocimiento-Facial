#importar dependencias
import cv2
import numpy as np
import face_recognition as fr
import sqlite3
from datetime import datetime
import os
from django.db import connections
import django

conn = sqlite3.connect('reconocimiento.db')

#extraer la conexión
cursor = conn.cursor()

# Consulta SQL para obtener datos de los usuarios
cursor.execute('SELECT Nombres, Apellidos, Foto FROM Usuarios')

#extraer los datos de la consulta
users_data = cursor.fetchall()

# Definir coordenadas iniciales
x1, y1, x2, y2 = 0, 0, 0, 0

# Declaración de colores para el recuadro en camara
color_verde = (0, 255, 0)  # R, G, B para verde
color_rojo = (0, 0, 255)  # R, G, B para rojo

# variable de tiempo
ultima_hora_registro = None

#variable de acceso
Acceso = 0

# funcion para capturar la fecha y hora de reconocimiento
def registrar_registro(usuario_id):
    global ultima_hora_registro # instanciar variable global de hora
    hora_actual = datetime.now() # optener la fecha y hora del sistema
    hora_entrada = hora_actual.strftime('%Y-%m-%d %H:%M:%S') # entregar la fecha y hora
    
    # Verificar si ha pasado al menos 10 segundos desde el último registro
    if ultima_hora_registro is None or (hora_actual - ultima_hora_registro).total_seconds() >= 10:
        # Insertar el registro en la tabla Registros
        cursor.execute("INSERT INTO Registros (UsuarioID, Fecha) VALUES (?, ?)", (usuario_id, hora_entrada))
        conn.commit() # guardar cambios
        ultima_hora_registro = hora_actual # comparar horas (verificar si genera otro registro o no)

# Llamar la cámara
cap = cv2.VideoCapture(0)

# inicializar las dimenciones del recuadro
x1, y1, x2, y2 = 0, 0, 0, 0

# iniciar el proceso de reconocimiento
while True:
    # empezar a leer y caprutar el frame
    ret, frame = cap.read()
    # redimencionar 
    frame2 = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    # convertir de BGR A RGB
    rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
    # instanciar el rostro con el nuevo color
    faces = fr.face_locations(rgb)
    # codificar el rostro
    facesCod = fr.face_encodings(rgb, faces)
    
    hora_actual = datetime.now() # obtener la fecha y hora del sistema

    for faceCod, faceloc in zip(facesCod, faces):
        x1, y1, x2, y2 = faceloc  # Obtener las coordenadas originales
        # Calcular nuevas coordenadas
        x1 -= 20  # Restar 20 a x1
        y1 -= 20  # Restar 20 a y1
        x2 += 20  # Sumar 40 a x2
        y2 += 20  # Sumar 40 a y2
        
        match = False # instanciar 
        
        for user_data in users_data: # extraer la informacion del usuario
            nombre = user_data[0] # estraer el nombre
            apellido = user_data[1] # estraer el apellido
            foto_path = user_data[2] # estraer la foto (LA RUTA DE LA FOTO)
            known_image = fr.load_image_file(foto_path) # cargar ruta de la foto
            known_face_encoding = fr.face_encodings(known_image)[0] # 

            results = fr.compare_faces([known_face_encoding], faceCod)
            # print(f"Comparación para {nombre}: {results[0]}") # me envia un mensaje de comparacion por cada usuario en la base de datos

            if results[0]: #
                match = True
                break

        if match:
            y1, x2, y2, x1 = faceloc
            # Redimensionar las coordenadas
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            r, g, b = (0, 255, 0)  # Color verde
            # capturar rostro en un recuadro y darle color verdo y mostraer el nombre
            cv2.rectangle(frame, (x1, y1), (x2, y2), (r, g, b), 2)
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (r, g, b), cv2.FILLED)
            cv2.putText(frame, nombre, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            print(f'Usuario reconocido: {nombre}') # mostraer el nombre del usuario reconocido (en consola)
            
            # declarar si tiene acceso o no
            Acceso = 1
            if Acceso == 1:
                print('Acceso Permitido')
            else:
                print('Acceso Denegado')
            
            # agregar un registro a la tabla (REGISTROS) de la BBDD cada 10 seundos (si es el mismo rostro)
            cursor.execute("SELECT ID FROM Usuarios WHERE Nombres = ?", (nombre,))
            result = cursor.fetchone()
            if result:
                usuario_id = result[0]
                registrar_registro(usuario_id)
        else:
            # Si no se detecta un rostro conocido, pintar un cuadro rojo con "desconocido"
            # Obtener las coordenadas
            y1, x2, y2, x1 = faceloc
            # Redimensionar las coordenadas
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            r, g, b = color_rojo # Color Rojo
            # capturar rostro en un recuadro y darle color verdo y mostraer la palabra "DESCONOCIDO"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (r, g, b), 1)
            cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (r, g, b), cv2.FILLED)
            cv2.putText(frame, "Desconocido", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            print('Usuario No Reconocido') # mostraer que el usuario no fue reconocido (en consola)
            
            # declarar si tiene acceso o no
            Acceso = 0
            if Acceso == 1:
                print('Acceso Permitido')
            else:
                print('Acceso Denegado')

    cv2.imshow('RECONOCIMIENTO FACIAL', frame) # titulo del frame

    # establecer que si se preciola la tecla esc se termina la ejecucion
    t = cv2.waitKey(1) 
    if t == 27:
        break

# definir acceso a las instalaciones
AccesoInstalaciones = Acceso
print(f'El Acceso es: {AccesoInstalaciones}')

# cerrar la ventana
cap.release()
cv2.destroyAllWindows()
