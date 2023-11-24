'''
reconocimiento facial usanfo Mediapipe para la mallafacial y recococimiento, cv2 para la camara, cuadro y nombre en camara y face_recognition para el reconocimiento facial.
con la version #2 del script.
'''

# importar dependencias
import mediapipe as mp
import cv2
import sqlite3
from datetime import datetime
import os
import face_recognition as fr



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

# capturar la camara
cap = cv2.VideoCapture(0)

# iniciar la deteccion
with mp_face_detection.FaceDetection(
    min_detection_confidence=0.5) as face_detection , mp_face_mesh.FaceMesh(
        min_detection_confidence=0.5,
        max_num_faces=9,
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
        users_encodings = []
        for user_data in users_data:
            foto_path = user_data[2] # estraer la foto (LA RUTA DE LA FOTO)
            known_image_path = os.path.join(main_directory, media_directory, foto_path) # complemento de la ruta raiz con la ruta de la foto
            known_image = fr.load_image_file(known_image_path) # cargar ruta de la foto
            known_face_encoding = fr.face_encodings(known_image)[0] # 
            users_encodings.append((user_data[0], user_data[1], known_face_encoding))

        # En tu bucle principal
        results = face_detection.process(frame_rgb) # optener resultados
        # si logra alguna deteción
        if results.detections is not None:
            # para cada detección
            for i, detection in enumerate(results.detections):
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
                if len(encodings) > i: # Solo proceder si se encontró al menos una cara
                    encoding = encodings[i]
                    
                    # Comparar esta codificación con las de la base de datos
                    for nombre, apellido, known_face_encoding in users_encodings:
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
                                    
                
        # mostrar el video stream en pantalla
        cv2.imshow("FRAME", frame) # titulo y frame usado
        
        # establever que precione esc para salir
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

# cerrar todo
cap.release()
cv2.destroyAllWindows()