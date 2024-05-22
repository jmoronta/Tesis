import pymysql
from datetime import datetime

# Conectarse a la base de datos
conexion = pymysql.connect(
     host="localhost", 
    user="kbza",
    password="kbza52",
    db="registros_patentes"
)

cursor = conexion.cursor()

# Supongamos que tienes una tabla llamada 'datos' con las columnas mencionadas anteriormente

# Obtener la fecha y hora actual
fecha_hora_actual = datetime.now()

# Obtener los datos de la imagen, la URL y la cadena
imagen_data = open('./file.png', 'rb').read()  # Reemplaza 'ruta/a/imagen.jpg' con la ruta de tu imagen
url = "https://ejemplo.com"  # Reemplaza "https://ejemplo.com" con tu URL
cadena = "Ejemplo de cadena"  # Reemplaza "Ejemplo de cadena" con tu cadena

# Insertar los datos en la tabla
consulta = "INSERT INTO patentes(created,image,ubicacion,id_patente) VALUES (%s, %s, %s, %s)"
datos = (fecha_hora_actual, imagen_data, url, cadena)
cursor.execute(consulta, datos)

# Confirmar la operación
conexion.commit()

# Cerrar conexión
cursor.close()
conexion.close()