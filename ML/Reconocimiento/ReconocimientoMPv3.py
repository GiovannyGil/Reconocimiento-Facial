import mediapipe as mp
import cv2
import sqlite3
import os
import face_recognition as fr

# Variables globales
main_directory = os.path.dirname(os.path.abspath(__file__))
media_directory = 'fotos/'
database_directory = 'reconocimiento.db'
face_detection = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)
face_mesh = mp.solutions.face_mesh.FaceMesh(min_detection_confidence=0.5, max_num_faces=9, min_tracking_confidence=0.5)


def cargar_datos_usuarios():
    conn = sqlite3.connect(os.path.join(main_directory, database_directory))
    cursor = conn.cursor()
    cursor.execute('SELECT Nombres, Apellidos, Foto FROM Usuarios')
    return cursor.fetchall()


def cargar_codificaciones_usuarios(users_data):
    users_encodings = []
    for user_data in users_data:
        foto_path = user_data[2]
        known_image_path = os.path.join(main_directory, media_directory, foto_path)
        known_image = fr.load_image_file(known_image_path)
        known_face_encoding = fr.face_encodings(known_image)[0]
        users_encodings.append((user_data[0], user_data[1], known_face_encoding))
    return users_encodings


def dibujar_cuadro_y_nombre(frame, xmin, ymin, w, h, color, nombre):
    cv2.rectangle(frame, (xmin, ymin), (xmin + w, ymin + h), color, 2)
    cv2.putText(frame, nombre, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 1)
    print(nombre)


def reconocer_y_dibujar(frame, users_encodings):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(frame_rgb)
    if results.detections is not None:
        for i, detection in enumerate(results.detections):
            xmin, ymin, w, h = obtener_cordenadas(frame, detection)
            face = frame[ymin:ymin + h, xmin:xmin + w]
            if face.size == 0:
                continue
            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            encodings = fr.face_encodings(face_rgb)
            if len(encodings) > i:
                encoding = encodings[i]
                comparar_codificaciones(encoding, users_encodings, frame, xmin, ymin, w, h)


def obtener_cordenadas(frame, detection):
    height, width, _ = frame.shape
    xmin = int(detection.location_data.relative_bounding_box.xmin * width)
    ymin = int(detection.location_data.relative_bounding_box.ymin * height)
    w = int(detection.location_data.relative_bounding_box.width * width)
    h = int(detection.location_data.relative_bounding_box.height * height)
    return xmin, ymin, w, h


def comparar_codificaciones(encoding, users_encodings, frame, xmin, ymin, w, h):
    for nombre, apellido, known_face_encoding in users_encodings:
        match = fr.compare_faces([known_face_encoding], encoding)
        if match[0]:
            dibujar_cuadro_y_nombre(frame, xmin, ymin, w, h, (0, 255, 0), nombre)
        else:
            dibujar_cuadro_y_nombre(frame, xmin, ymin, w, h, (0, 0, 255), 'Desconocido')


def mostrar_video_stream(frame):
    cv2.imshow("FRAME", frame)
    k = cv2.waitKey(1) & 0xFF
    return k


def main():
    cap = cv2.VideoCapture(0)
    users_data = cargar_datos_usuarios()
    users_encodings = cargar_codificaciones_usuarios(users_data)

    while True:
        ret, frame = cap.read()
        if ret == False:
            break

        frame = cv2.flip(frame, 1)
        k = mostrar_video_stream(frame)

        if k == 27:
            break

        reconocer_y_dibujar(frame, users_encodings)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
