import cv2
import numpy as np
import face_recognition as fr
import sqlite3
from datetime import datetime
import os.path

main_directory = os.path.dirname(os.path.abspath(__file__))
media_directory = 'media/'
database_directory = 'ReconocimientoF.db'

conn = sqlite3.connect(os.path.join(main_directory, database_directory))
cursor = conn.cursor()
cursor.execute('SELECT nombres, apellidos, foto FROM usuarios_persona')
users_data = cursor.fetchall()

x1, y1, x2, y2 = 0, 0, 0, 0
color_verde = (0, 255, 0)
color_rojo = (0, 0, 255)
ultima_hora_registro = None
Acceso = 0

def registrar_registro(usuario_id):
    global ultima_hora_registro
    hora_actual = datetime.now()
    hora_entrada = hora_actual.strftime('%Y-%m-%d %H:%M:%S')

    if ultima_hora_registro is None or (hora_actual - ultima_hora_registro).total_seconds() >= 10:
        cursor.execute("INSERT INTO usuarios_registros (UsuarioID_id, fecha) VALUES (?, ?)", (usuario_id, hora_entrada))
        conn.commit()
        ultima_hora_registro = hora_actual

def cargar_usuarios():
    cursor.execute('SELECT nombres, apellidos, foto FROM usuarios_persona')
    return cursor.fetchall()

def detectar_rostros(frame):
    frame2 = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
    faces = fr.face_locations(rgb)
    facesCod = fr.face_encodings(rgb, faces)
    return faces, facesCod

def dibujar_recuadro(frame, faceloc, color, text=''):
    y1, x2, y2, x1 = faceloc
    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
    cv2.putText(frame, text, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

def cargar_y_comparar_rostro(user_data, faceCod):
    nombre, apellido, foto_path = user_data
    known_image_path = os.path.join(main_directory, media_directory, foto_path)
    known_image = fr.load_image_file(known_image_path)
    known_face_encoding = fr.face_encodings(known_image)[0]

    results = fr.compare_faces([known_face_encoding], faceCod)
    return results[0]

def procesar_resultado(match, frame, faceloc, color, nombre):
    if match:
        #dibujar_recuadro(frame, faceloc, color, nombre)
        print(f'Usuario reconocido: {nombre}')
        Acceso = 1
        print('Acceso Permitido' if Acceso == 1 else 'Acceso Denegado')
        cursor.execute("SELECT ID FROM usuarios_persona WHERE nombres = ?", (nombre,))
        result = cursor.fetchone()
        if result:
            usuario_id = result[0]
            registrar_registro(usuario_id)
    else:
        #dibujar_recuadro(frame, faceloc, color_rojo, 'Desconocido')
        print('Usuario No Reconocido')
        Acceso = 0
        print('Acceso Permitido' if Acceso == 1 else 'Acceso Denegado')

def reconocer_rostro(frame, users_data, facesCod, faces):
    global Acceso
    for faceCod, faceloc in zip(facesCod, faces):
        x1, y1, x2, y2 = faceloc
        x1 -= 20
        y1 -= 20
        x2 += 20
        y2 += 20

        match = False

        for user_data in users_data:
            match = cargar_y_comparar_rostro(user_data, faceCod)
            if match:
                break

        procesar_resultado(match, frame, faceloc, color_verde, user_data[0])


def main():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()

        faces, facesCod = detectar_rostros(frame)
        reconocer_rostro(frame, users_data, facesCod, faces)

        cv2.imshow('RECONOCIMIENTO FACIAL', frame)

        t = cv2.waitKey(1)
        if t == 27:
            break

    AccesoInstalaciones = Acceso
    print(f'El Acceso es: {AccesoInstalaciones}')

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
