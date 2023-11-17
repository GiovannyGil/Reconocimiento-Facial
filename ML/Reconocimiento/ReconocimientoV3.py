#importar dependencias
import cv2
import numpy as np
import face_recognition as fr
import sqlite3
from datetime import datetime
import os
import sqlite3
import mediapipe as mp


mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


conn = sqlite3.connect('reconocimiento.db')

#extraer la conexión
cursor = conn.cursor()

# Consulta SQL para obtener datos de los usuarios
cursor.execute('SELECT Nombres, Apellidos, Foto FROM Usuarios')

#extraer los datos de la consulta
users_data = cursor.fetchall()

# Captura video por la cámara
cap = cv2.VideoCapture(0)

# Inicializa Face Recognition
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

with mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=5,
    min_detection_confidence=0.5) as face_mesh:
    
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        faces = face_cascade.detectMultiScale(frame_rgb, 1.5, 5)
        
        frame_copy = frame.copy()

        for (x, y, w, h) in faces:
            x -= 25
            y -= 25
            w += 50
            h += 50
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        if results.multi_face_landmarks is not None:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame_copy, face_landmarks,    
                    mp_face_mesh.FACE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=1, circle_radius=1),
                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1))
        
        cv2.imshow("RECONOCIMIENTO FACIAL", frame_copy)

        # establecer que si se preciola la tecla esc se termina la ejecucion
        t = cv2.waitKey(1) 
        if t == 27:
            break

cap.release()
cv2.destroyAllWindows()
conn.close()
