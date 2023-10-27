import cv2
import mediapipe as mp
import os

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


# carpeta donde se almacenaran los fotos de los rostros
OutPut = './fotos'
# si no existe la carpeta, creala
if not os.path.exists(OutPut):
    os.makedirs(OutPut, exist_ok=True)
# os.makedirs(OutPut, exist_ok=True)


# CONTADOR PARA LAS IMAGENES 'ID' UNICO
photo_counter = 0


# captura video por camara
cap = cv2.VideoCapture(0)
# Inicializa Face Recognition
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

with mp_face_mesh.FaceMesh(
    static_image_mode=False, # True para imagenes fotos, false para video, stream
    max_num_faces=3, # cantidad de personas a las que le pondra la malla facial
    min_detection_confidence=0.5) as face_mesh:
    
    while True:
        ret, frame = cap.read()
        if ret == False:
            break
        frame = cv2.flip(frame,1) # ver la salida por camara como espejo
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        faces = face_cascade.detectMultiScale(frame_rgb, scaleFactor=1.1, minNeighbors=5)
        
        for (x, y, w, h) in faces:
            # Ajusta el tamaño de la región de interés (ROI)
            x -= 10  # Reduce la coordenada x (izquierda)
            y -= 10  # Reduce la coordenada y (arriba)
            w += 20  # Aumenta el ancho
            h += 20  # Aumenta la altura
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        
        
        if results.multi_face_landmarks is not None: # comprovar que no es vacio, que haya rostros
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame, face_landmarks,    
                    mp_face_mesh.FACE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0,0,0), thickness=1, circle_radius=1), mp_drawing.DrawingSpec(color=(255,255,255), thickness=1)) # ver los puntos y conecciones en la imagen con colores modificados
        cv2.imshow("Frame", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
cap.release()
cv2.destroyAllWindows()
