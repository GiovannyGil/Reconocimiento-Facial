import cv2
import os
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

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
        # frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        faces = face_cascade.detectMultiScale(frame_rgb, 1.3, 5)
        
        frame_copy = frame.copy()  # Copia del cuadro de la cámara para dibujar elementos visuales

        for (x, y, w, h) in faces:
            x -= 10
            y -= 10
            w += 20
            h += 20
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        if results.multi_face_landmarks is not None:
            for face_landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(frame_copy, face_landmarks,    
                    mp_face_mesh.FACE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 0), thickness=1, circle_radius=1),
                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1))
        
        cv2.imshow("Frame", frame_copy)  # Muestra la copia del cuadro con elementos visuales

        # Espera a que el usuario presione una tecla
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('s'):  # Si el usuario presiona 's', toma la foto
            face_photo = frame[y:y+h, x:x+w]  # Recorta solo la región del rostro
            print("Ingrese el nombre de la imagen:")
            photo_name = input()  # Solicita el nombre de la imagen por consola
            if not photo_name:
                photo_name = "rostro"  # Asigna un nombre predeterminado si no se proporciona uno
            photo_name = os.path.join("/home/jorge/Documentos/Sistema-Reconocimiento-Facial-Instalaciones/ML/fotos", f'{photo_name}.jpg')
            cv2.imwrite(photo_name, face_photo)  # Guarda la foto del rostro
            print(f"Imagen guardada como {photo_name}")
            break

cap.release()
cv2.destroyAllWindows()
