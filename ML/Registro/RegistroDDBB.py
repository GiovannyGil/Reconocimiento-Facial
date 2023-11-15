import cv2
import os
import sqlite3
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Conexión a la base de datos SQLite (asegúrate de que la ruta sea válida)
db_connection = sqlite3.connect('reconocimiento.db')
cursor = db_connection.cursor()

# Crear la tabla si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Nombres TEXT,
        Apellidos TEXT,
        Documento TEXT,
        Foto TEXT,
        TipoUsuarioID INTEGER
    )
''')
db_connection.commit()

# Captura video por la cámara
cap = cv2.VideoCapture(0)

# Inicializa Face Recognition
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

with mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=3,
    min_detection_confidence=0.5) as face_mesh:
    
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        faces = face_cascade.detectMultiScale(frame_rgb, 1.3, 5)
        
        frame_copy = frame.copy()

        for (x, y, w, h) in faces:
            # x -= 10
            # y -= 10
            # w += 20
            # h += 20
            x -= 50
            y -= 50
            w += 100
            h += 100
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        if results.multi_face_landmarks is not None:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame_copy, face_landmarks,    
                    mp_face_mesh.FACE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=1, circle_radius=1),
                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1))
        
        cv2.imshow("Frame", frame_copy)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('s'):
            face_photo = frame[y:y+h, x:x+w]
            print("Ingrese el nombre:")
            nombres = input()
            print("Ingrese los apellidos:")
            apellidos = input()
            print("Ingrese el número de documento:")
            documento = input()
            print("Ingrese el TipoUsuarioID (1 o 2):")
            tipo_usuario_id = int(input())

            # Guardar la información en la base de datos
            photo_name = f'{nombres}_{apellidos}_{documento}'
            photo_path = os.path.join("/home/jorge/Documentos/Sistema-Reconocimiento-Facial-Instalaciones/ML/fotos", f'{nombres}.jpg')
            cv2.imwrite(photo_path, face_photo)
            
            # Insertar datos en la base de datos
            cursor.execute('''
                INSERT INTO Usuarios (Nombres, Apellidos, Documento, Foto, TipoUsuarioID)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombres, apellidos, documento, photo_path, tipo_usuario_id))
            db_connection.commit()
            
            print(f"Registro guardado en la base de datos con ID {cursor.lastrowid}")
            break

cap.release()
cv2.destroyAllWindows()
db_connection.close()
