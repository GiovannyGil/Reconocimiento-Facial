'''
protocolo de deteccion de rostros y malla facial junto con reconocimiento facial
'''

# importar dependencias
import mediapipe as mp
import cv2
import sqlite3
from datetime import datetime
import os

# instancias las variables de deteccion de rostros y dibujo en el rostro
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
# variable de iniciacion de la malla facial
mp_face_mesh = mp.solutions.face_mesh

# capturar la camara
cap = cv2.VideoCapture(0)

# iniciar la deteccion
with mp_face_detection.FaceDetection(
    min_detection_confidence=0.5) as face_detection , mp_face_mesh.FaceMesh(
        min_detection_confidence=0.5,
        max_num_faces=5,
        min_tracking_confidence=0.5) as face_mesh:
    
    # iniciar el video stream
    while True:
        ret, frame = cap.read() # capturar el frame del stream
        if ret == False: # si no hay stream cerrar
            break
        
        frame = cv2.flip(frame, 1) # hacer la camra tipo espejo
        # cambiar colores de BGR a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        height, width, _ = frame.shape # capturar tamaño
        
        results = face_detection.process(frame_rgb) # optener resultados
        
        # si logra alguna deteción
        if results.detections is not None:
            # para cada tecion
            for detection in results.detections:
                '''mp_drawing.draw_detection(frame, detection, 
                mp_drawing.DrawingSpec(color=(0,0,0), circle_radius=5),
                mp_drawing.DrawingSpec(color=(0,0,0)))'''
                
                # obtener las cordenadas para pintar el cuadro
                xmin = int(detection.location_data.relative_bounding_box.xmin * width)
                ymin = int(detection.location_data.relative_bounding_box.ymin * height)
                w = int(detection.location_data.relative_bounding_box.width * width)
                h = int(detection.location_data.relative_bounding_box.height * height)
                
                # pintar el cuadro de negro si hay rostros
                cv2.rectangle(frame, (xmin, ymin), (xmin + w, ymin + h), (0,0,0,),2)
                
                # Detección de malla facial
                results_mesh = face_mesh.process(frame_rgb)
                if results_mesh.multi_face_landmarks:
                    for face_landmarks in results_mesh.multi_face_landmarks:
                        mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=1, circle_radius=1),
                        mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1))
                
        # mostrar el video stream en pantalla
        cv2.imshow("FRAME", frame) # titulo y frame usado
        
        # establever que precione esc para salir
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

# cerrar todo
cap.release()
cv2.destroyAllWindows()