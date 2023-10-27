import sqlite3

# Conectarse a la base de datos (o crearla si no existe)
conn = sqlite3.connect("reconocimiento.db")
cursor = conn.cursor()

# Crear la tabla TipoUsuario
cursor.execute("""
CREATE TABLE IF NOT EXISTS TipoUsuario (
    ID INTEGER PRIMARY KEY,
    Nombre TEXT,
    Descripcion TEXT
)
""")

# Crear la tabla Usuarios con la clave foránea TipoUsuarioID
cursor.execute("""
CREATE TABLE IF NOT EXISTS Usuarios (
    ID INTEGER PRIMARY KEY,
    Nombres TEXT,
    Apellidos TEXT,
    Documento TEXT,
    Foto BLOB,
    TipoUsuarioID INTEGER,
    FOREIGN KEY (TipoUsuarioID) REFERENCES TipoUsuario(ID)
)
""")


# Crear la tabla Entradas
cursor.execute("""
CREATE TABLE IF NOT EXISTS Registros (
    ID INTEGER PRIMARY KEY,
    UsuarioID INTEGER,
    Fecha DATETIME,
    FOREIGN KEY (UsuarioID) REFERENCES Usuarios(ID)
)
""")

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()


""" 

Recuerda que para insertar imágenes en la tabla Usuarios, primero debes cargar la imagen, convertirla a bytes y luego insertarla en la base de datos. Aquí tienes un ejemplo de cómo hacerlo:

# Cargar una imagen y convertirla a bytes
with open('imagen.jpg', 'rb') as f:
    imagen_bytes = f.read()

# Insertar la imagen en la tabla Usuarios
cursor.execute("INSERT INTO Usuarios (Nombres, Apellidos, Documento, Foto) VALUES (?, ?, ?, ?)", ('Nombre', 'Apellido', 'Documento', sqlite3.Binary(imagen_bytes))

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()

"""