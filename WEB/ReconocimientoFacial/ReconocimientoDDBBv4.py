#importar dependencias
import cv2
import face_recognition as fr
import sqlite3
from datetime import datetime
import os.path
import time
import Jetson.GPIO as GPIO

# ruta principal
main_directory = os.path.dirname(os.path.abspath(__file__)) # obtener la ruta principal dinamicamente en cualquier sitio y S.O

# ruta para ir a la media => ubicacion de las fotos
media_directory = 'media/'

# ruta de la base de datos
database_directory = 'ReconocimientoF.db'

# ruta dinamica de la base de datos
conn = sqlite3.connect(os.path.join(main_directory, database_directory))
cursor = conn.cursor()

# Definir coordenadas iniciales
x1, y1, x2, y2 = 0, 0, 0, 0

# Declaración de colores para el recuadro en camara
color_verde = (0, 255, 0)  # B, G, R para verde
color_rojo = (0, 0, 255)  # B, G, R para rojo

# variable de tiempo
ultima_hora_registro = None

# Llamar la cámara
cap = cv2.VideoCapture(0)

# inicializar las dimenciones del recuadro
x1, y1, x2, y2 = 0, 0, 0, 0

# funcion para conexion a la base de datos
def conectar():
    # Consulta SQL para obtener datos de los usuarios
    cursor.execute('SELECT nombres, apellidos, foto FROM usuarios_persona')

    #extraer los datos de la consulta
    users_data = cursor.fetchall()
    return users_data

# funcion para capturar la fecha y hora de reconocimiento
def registrar_registro(usuario_id):
    global ultima_hora_registro # instanciar variable global de hora
    hora_actual = datetime.now() # optener la fecha y hora del sistema
    hora_entrada = hora_actual.strftime('%Y-%m-%d %H:%M:%S') # entregar la fecha y hora
    
    # Verificar si ha pasado al menos 10 segundos desde el último registro
    if ultima_hora_registro is None or (hora_actual - ultima_hora_registro).total_seconds() >= 10:
        # Insertar el registro en la tabla Registros
        cursor.execute("INSERT INTO usuarios_registros (UsuarioID_id, fecha) VALUES (?, ?)", (usuario_id, hora_entrada))
        conn.commit() # guardar cambios
        ultima_hora_registro = hora_actual # comparar horas (verificar si genera otro registro o no)
        
# funcion para detectar rostros
def detectar_rostros(frame):
    frame2 = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)
    faces = fr.face_locations(rgb)
    facesCod = fr.face_encodings(rgb, faces)
    return faces, facesCod

# funcion para dibujar el recuadro
def dibujar_recuadro(frame, faceloc, color, text=''):
    y1, x2, y2, x1 = faceloc
    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.rectangle(frame, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
    cv2.putText(frame, text, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

# funcion para extraer la informacion
def cargar_y_comparar_rostro(users_data, faceCod):
    for user_data in users_data: # extraer la informacion del usuario
        nombre = user_data[0] # estraer el nombre
        apellido = user_data[1] # estraer el apellido
        foto_path = user_data[2] # estraer la foto (LA RUTA DE LA FOTO)
        known_image_path = os.path.join(main_directory, media_directory, foto_path) # complemento de la ruta raiz con la ruta de la foto
        known_image = fr.load_image_file(known_image_path) # cargar ruta de la foto
        known_face_encoding = fr.face_encodings(known_image)[0] # 

        results = fr.compare_faces([known_face_encoding], faceCod)
        # print(f"Compa

        if results[0]: #
            match = True
            break
    return nombre, match

def pulso(Acceso):
    if Acceso == 1:
        print(f'Acceso Permitido {Acceso}')

        # enviar pulso 
        PIN = 7
        try:
            # configurar el modo del pin como salida
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(PIN, GPIO.OUT)
    
            # Enviar un pulso de 5V durante 5 segundos
            GPIO.output(PIN, GPIO.HIGH)
            time.sleep(15) # esperar 5 segundos
            GPIO.output(PIN, GPIO.LOW)
        finally:
            # limpiar losp ines GPIO al finalizar
            GPIO.cleanup()
    
    else:
        print(f'Acceso Denegado  {Acceso}')

# funcion para detectar el match
def Match(nombre, match, frame, faceloc, color):
    if match:
        dibujar_recuadro(frame, faceloc, color, nombre)
        print(f'Usuario reconocido: {nombre}')
        Acceso = 1
        pulso(Acceso)
                
        # agregar un registro a la tabla (REGISTROS) de la BBDD cada 10 seundos (si es el mismo rostro)
        cursor.execute("SELECT ID FROM usuarios_persona WHERE nombres = ?", (nombre,))
        result = cursor.fetchone()
        if result:
            usuario_id = result[0]
            registrar_registro(usuario_id)
    else:
        dibujar_recuadro(frame, faceloc, color_rojo, 'Desconocido')
        print('Usuario No Reconocido')
        Acceso = 0 # instanciar variable en 0
        pulso(Acceso)
        
    # Puedes ajustar el tiempo de espera según las necesidades
    time.sleep(1)
    

# funcion principal
def main():
    global Acceso
    while True:
        # Capturar frame por frame
        ret, frame = cap.read()
        # Detectar rostros
        faces, facesCod = detectar_rostros(frame)
        # Conectar a la base de datos
        users_data = conectar()
        # Recorrer los rostros detectados
        for faceCod, faceloc in zip(facesCod, faces):
            # Cargar y comparar rostro
            nombre, match = cargar_y_comparar_rostro(users_data, faceCod)
            # Dibujar recuadro
            Match(nombre, match, frame, faceloc, color_verde)
            
        # Mostrar frame
        cv2.imshow('RECONOCIMIENTO FACIAL', frame)
        # Salir con ESC
        t = cv2.waitKey(1)
        if t == 27:
            break
    
    # Liberar la cámara
    cap.release()
    # Cerrar todas las ventanas
    cv2.destroyAllWindows()
    # Cerrar la conexión a la base de datos
    conn.close()
    
# Ejecutar el programa
if __name__ == "__main__":
    main()
    
