import cv2
import face_recognition as fr
import threading
import sqlite3
from datetime import datetime

# ...

conn = sqlite3.connect('reconocimiento.db')
cursor = conn.cursor()
cursor.execute('SELECT Nombres, Apellidos, Foto FROM Usuarios')
users_data = cursor.fetchall()

x1, y1, x2, y2 = 0, 0, 0, 0
color_verde = (0, 255, 0)
color_rojo = (0, 0, 255)
ultima_hora_registro = None
Acceso = 0

def registrar_registro(usuario_id, conn):
    global ultima_hora_registro
    cursor = conn.cursor()
    hora_actual = datetime.now()
    hora_entrada = hora_actual.strftime('%Y-%m-%d %H:%M:%S')
    
    if ultima_hora_registro is None or (hora_actual - ultima_hora_registro).total_seconds() >= 10:
        cursor.execute("INSERT INTO Registros (UsuarioID, Fecha) VALUES (?, ?)", (usuario_id, hora_entrada))
        conn.commit()
        ultima_hora_registro = hora_actual
        
        
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def reconocimiento_facial():
    global ultima_hora_registro, Acceso
    conn = sqlite3.connect('reconocimiento.db')

    while True:
        ret, frame = cap.read()

        if not ret:
            continue  # Ignorar el frame si la captura no tiene éxito

        frame2 = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
        faces = fr.face_locations(rgb)
        facesCod = fr.face_encodings(rgb, faces)

        hora_actual = datetime.now()

        cursor = conn.cursor()  # Mover la creación del cursor aquí

        for faceCod, faceloc in zip(facesCod, faces):
            x1, y1, x2, y2 = faceloc
            x1 -= 20
            y1 -= 20
            x2 += 20
            y2 += 20
            
            match = False
            
            for user_data in users_data:
                nombre = user_data[0]
                apellido = user_data[1]
                foto_path = user_data[2]
                known_image = fr.load_image_file(foto_path)
                known_face_encoding = fr.face_encodings(known_image)[0]
                results = fr.compare_faces([known_face_encoding], faceCod)

                if results[0]:
                    match = True
                    break

            if match:
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                r, g, b = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (r, g, b), 2)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (r, g, b), cv2.FILLED)
                cv2.putText(frame, nombre, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                print(f'Usuario reconocido: {nombre}')
                
                Acceso = 1
                if Acceso == 1:
                    print('Acceso Permitido')
                else:
                    print('Acceso Denegado')

                cursor.execute("SELECT ID FROM Usuarios WHERE Nombres = ?", (nombre,))
                result = cursor.fetchone()
                if result:
                    usuario_id = result[0]
                    registrar_registro(usuario_id, conn)
            else:
                y1, x2, y2, x1 = faceloc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                r, g, b = color_rojo
                cv2.rectangle(frame, (x1, y1), (x2, y2), (r, g, b), 1)
                cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), (r, g, b), cv2.FILLED)
                cv2.putText(frame, "Desconocido", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                print('Usuario No Reconocido')
                
                Acceso = 0
                if Acceso == 1:
                    print('Acceso Permitido')
                else:
                    print('Acceso Denegado')

        cv2.imshow('RECONOCIMIENTO FACIAL', frame)
        cursor.close()

        t = cv2.waitKey(1)
        if t == 27:
            break

    conn.close()

# Antes del bucle principal
reconocimiento_thread = threading.Thread(target=reconocimiento_facial)
reconocimiento_thread.start()

while True:
    ret, frame = cap.read()

    # No hay operaciones adicionales con el frame sin procesar en este punto

    t = cv2.waitKey(1)
    if t == 27:
        break

cap.release()
cv2.destroyAllWindows()
reconocimiento_thread.join()
