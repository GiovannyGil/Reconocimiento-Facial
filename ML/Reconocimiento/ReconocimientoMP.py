'''
reconocimiento facial usanfo Mediapipe para la mallafacial y recococimiento, cv2 para la camara, cuadro y nombre en camara y face_recognition para el reconocimiento facial.
con la version #1 del script.
'''

# importar dependencias
import mediapipe as mp
import cv2
import sqlite3
from datetime import datetime
import os
import face_recognition as fr
import numpy as np

# instancias las variables de deteccion de rostros y dibujo en el rostro
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
# variable de iniciacion de la malla facial
mp_face_mesh = mp.solutions.face_mesh

# ruta principal
main_directory = os.path.dirname(os.path.abspath(__file__)) # obtener la ruta principal dinamicamente en cualquier sitio y S.O

# ruta para ir a la media => ubicacion de las fotos
# /home/jorge/Documentos/Sistema-Reconocimiento-Facial-Instalaciones/
media_directory = 'fotos/'
database_directory = 'reconocimiento.db'

# Crear conexión a la base de datos
conn = sqlite3.connect(os.path.join(main_directory, database_directory))
cursor = conn.cursor()

# Consulta SQL para obtener datos de los usuarios
cursor.execute('SELECT Nombres, Apellidos, Foto FROM Usuarios')

#extraer los datos de la consulta
users_data = cursor.fetchall()

# crear funcion para que pida por camara que mueva la cara y pestañee para intentar hacer un mejor reconocimiento facial y verificar si sea una persona real y no una foto o video

# Función para calcular la distancia euclidiana entre dos puntos
def euclidean_distance(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.linalg.norm(a - b)


# Función para comprobar si la cara se mueve hacia los lados
FACE_MOVEMENT_THRESHOLD = 10  # Define the threshold for face movement

def check_face_orientation(landmarks_prev, landmarks_curr):
    # Calcular la distancia euclidiana entre los puntos de referencia de la nariz en dos momentos consecutivos
    nose_movement = euclidean_distance(landmarks_prev['nose_tip'][0], landmarks_curr['nose_tip'][0])

    # Si la distancia es mayor que un cierto umbral, la cara se ha movido
    if nose_movement > FACE_MOVEMENT_THRESHOLD:
        return True
    else:
        return False

# Función para comprobar si los ojos parpadean
EYE_BLINK_THRESHOLD = 0.2  # Define the threshold for eye blink movement

def check_eyes_open(landmarks_prev, landmarks_curr):
    # Calcular la distancia euclidiana entre los puntos de referencia superior e inferior del ojo en dos momentos consecutivos
    left_eye_movement = euclidean_distance(landmarks_prev['left_eye'][1], landmarks_curr['left_eye'][1])
    right_eye_movement = euclidean_distance(landmarks_prev['right_eye'][1], landmarks_curr['right_eye'][1])

    # Si la distancia es mayor que un cierto umbral, los ojos han parpadeado
    if left_eye_movement > EYE_BLINK_THRESHOLD or right_eye_movement > EYE_BLINK_THRESHOLD:
        return True
    else:
        return False

# Función para comprobar si la persona es real
def comprobarPersonaReal(frame_prev, frame_curr):
    # Detectar los puntos de referencia faciales
    landmarks_prev = fr.face_landmarks(frame_prev)
    landmarks_curr = fr.face_landmarks(frame_curr)

    # Comprobar si se ha detectado al menos una cara
    if len(landmarks_prev) > 0 and len(landmarks_curr) > 0:
        # Comprobar si los ojos están abiertos y la cara está orientada hacia la cámara
        if check_eyes_open(landmarks_prev[0], landmarks_curr[0]) and check_face_orientation(landmarks_prev[0], landmarks_curr[0]):
            return True
        else:
            return False
    else:
        return False

# capturar la camara
cap = cv2.VideoCapture(0)

# iniciar la deteccion
with mp_face_detection.FaceDetection(
    min_detection_confidence=0.5) as face_detection, mp_face_mesh.FaceMesh(
        min_detection_confidence=0.5, max_num_faces=9, min_tracking_confidence=0.5) as face_mesh:
    
    # Capturar el primer frame
    ret, frame_prev = cap.read()

    # iniciar el video stream
    while True:
        ret, frame = cap.read() # capturar el frame del stream
        if ret == False: # si no hay stream cerrar
            break
        
        frame = cv2.flip(frame, 1) # hacer la camra tipo espejo
        # cambiar colores de BGR a RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Comprobar si la persona es real
        if comprobarPersonaReal(frame_prev, frame):
            print("Persona real detectada")
                    # El frame actual se convierte en el frame previo para la siguiente iteración
        frame_prev = frame
        
        height, width, _ = frame.shape # capturar tamaño
        
        results = face_detection.process(frame_rgb) # optener resultados
        
        # si logra alguna deteción
        if results.detections is not None:
            # para cada detección
            for detection in results.detections:
                # obtener las cordenadas para pintar el cuadro
                xmin = int(detection.location_data.relative_bounding_box.xmin * width)
                ymin = int(detection.location_data.relative_bounding_box.ymin * height)
                w = int(detection.location_data.relative_bounding_box.width * width)
                h = int(detection.location_data.relative_bounding_box.height * height)
                
                # Extraer la cara del frame usando las coordenadas
                face = frame[ymin:ymin+h, xmin:xmin+w]
                if face.size == 0:
                    continue
                
                # Convertir la imagen de BGR a RGB
                face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)

                # Codificar la cara usando un modelo de codificación facial
                encodings = fr.face_encodings(face_rgb)
                if len(encodings) > 0: # Solo proceder si se encontró al menos una cara
                    encoding = encodings[0]
                    
                    # Comparar esta codificación con las de la base de datos
                    for user_data in users_data:
                        nombre = user_data[0] # estraer el nombre
                        apellido = user_data[1] # estraer el apellido
                        foto_path = user_data[2] # estraer la foto (LA RUTA DE LA FOTO)
                        known_image_path = os.path.join(main_directory, media_directory, foto_path) # complemento de la ruta raiz con la ruta de la foto
                        known_image = fr.load_image_file(known_image_path) # cargar ruta de la foto
                        
                        known_face_encoding = fr.face_encodings(known_image)[0] # 
                        match = fr.compare_faces([known_face_encoding], encoding)
                        
                        # Encontrar la mejor coincidencia
                        if match[0]:
                            # Si la mejor coincidencia está por encima de un cierto umbral
                            nombre = user_data[0] # Asumiendo que el nombre y apellido están en las primeras dos columnas
                            # Dibujar un cuadro alrededor de la cara con el nombre del usuario correspondiente
                            cv2.rectangle(frame, (xmin, ymin), (xmin+w, ymin+h), (0, 255, 0), 2)
                            cv2.putText(frame, nombre, (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 1)
                    
                            # Detección de malla facial
                            results_mesh = face_mesh.process(frame_rgb)
                            if results_mesh.multi_face_landmarks:
                                for face_landmarks in results_mesh.multi_face_landmarks:
                                    mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=1, circle_radius=1),
                                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1))
                        else: 
                            
                            cv2.rectangle(frame, (xmin, ymin), (xmin+w, ymin+h), (0, 0, 255), 2)
                            cv2.putText(frame, 'Desconocido', (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 1)
                            
                            # Detección de malla facial
                            results_mesh = face_mesh.process(frame_rgb)
                            if results_mesh.multi_face_landmarks:
                                for face_landmarks in results_mesh.multi_face_landmarks:
                                    mp_drawing.draw_landmarks(frame, face_landmarks, mp_face_mesh.FACE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=1, circle_radius=1),
                                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1))
                                    
                
        else:
            print("No se detectó una persona real")


        # mostrar el video stream en pantalla
        cv2.imshow("FRAME", frame) # titulo y frame usado
        
        # establever que precione esc para salir
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

# cerrar todo
cap.release()
cv2.destroyAllWindows()