import cv2
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

with mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    min_detection_confidence=0.5) as face_mesh:
    
    image = cv2.imread('./fotos-Prueba/foto1.jpg')  # Lee la imagen
    height, width, _ = image.shape # tamaño
    #darle una imagen en RGB
    image_rgb=cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #aplicar deteccion
    results = face_mesh.process(image_rgb)
    
    print('Face Landmarks: ', results.multi_face_landmarks) 
    
    if results.multi_face_landmarks is not None: # asegurarse que si hay imagenes detectadas
        for face_landmarks in results.multi_face_landmarks: # lista de puntos del rostro detectado en cada iteracion
            mp_drawing.draw_landmarks(image, face_landmarks, mp_face_mesh.FACE_CONNECTIONS) # ver los puntos y conecciones en la imagen
    
    
    cv2.imshow('Image', image)  # Muestra la imagen
    cv2.waitKey(0)  # Espera a que se presione una tecla
cv2.destroyAllWindows()
