import pymysql
from datetime import datetime

def insert_en_tabla(imagen,patente,link):

    conexion = pymysql.connect(
        host="localhost", 
        user="root",
        password="password",
        db="registros_patentes"
    )
    cursor = conexion.cursor()

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now()

    # Obtener los datos de la imagen, la URL y la cadena
    imagen_data = open(imagen, 'rb').read()  
    url = link  
    cadena = patente  # Reemplaza "Ejemplo de cadena" con tu cadena
    #print("holaaaa:",link)
    
    # Insertar los datos en la tabla
    consulta = "INSERT INTO patente(fecha_hora,imagen,ubicacion,patente) VALUES (%s, %s, %s, %s)"
    datos = (fecha_hora_actual, imagen_data, url, cadena)
    cursor.execute(consulta, datos)

    # Confirmar la operación
    conexion.commit()

    # Cerrar conexión
    cursor.close()
    conexion.close()

def obtener_datos():
    try:
        # Establecer conexión con la base de datos
        conexion = pymysql.connect(
            host="localhost",
            user="root",
            password="password",
            db="registros_patentes"
        )
        with conexion.cursor() as cursor:
            # Ejecutar la consulta SELECT
            consulta = "SELECT * FROM patente"
            cursor.execute(consulta)
            # Obtener todos los registros
            datos = cursor.fetchall()
            return datos
    except pymysql.Error as e:
        print("Error al obtener datos de la tabla:", e)
    finally:
        # Cerrar la conexión
        conexion.close()