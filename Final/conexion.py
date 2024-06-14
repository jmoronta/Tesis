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
    linkfull=url[0]
    linklat=url[1]
    linklon=url[2] 
    cadena = patente  # Reemplaza "Ejemplo de cadena" con tu cadena
    #print("holaaaa:",link)
    
    # Insertar los datos en la tabla
    consulta = "INSERT INTO patente(fecha_hora,imagen,ubicacion,patente,latitud,longitud) VALUES (%s, %s, %s, %s, %s, %s)"
    datos = (fecha_hora_actual, imagen_data, linkfull, cadena,linklat,linklon)
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
        
        
def insertar_cobro(patente, tiempo, monto):
    try:
        conexion = pymysql.connect(
            host="localhost", 
            user="root",
            password="password",
            db="registros_patentes"
        )
        with conexion.cursor() as cursor:
            consulta2 = " INSERT INTO cobros (patente, tiempo, cobrar) VALUES (%s, %s, %s)"
            datos2 = (patente, tiempo, monto)    
            cursor.execute(consulta2,datos2 )
        
        # Confirmar la operación
        conexion.commit()
        cursor.close()
        
    except Exception as e:
        print(f"Error al insertar en la tabla cobros: {e}")
        
def dashboard_data():
    conexion = pymysql.connect(
            host="localhost", 
            user="root",
            password="password",
            db="registros_patentes"
        )
    with conexion.cursor() as cursor:
    # Obtener datos de la base de datos
    #cur = mysql.connection.cursor()
    
    # Contar la cantidad de patentes
        cursor.execute("SELECT COUNT(*) FROM patentes")
    cantidad_patentes = cursor.fetchone()[0]

    # Contar la cantidad de ubicaciones
    cursor.execute("SELECT COUNT(DISTINCT ubicacion) FROM patentes")
    cantidad_ubicaciones = cursor.fetchone()[0]

    # Sumar todos los cobros
    cursor.execute("SELECT SUM(monto) FROM cobros")
    suma_cobros = cursor.fetchone()[0] or 0  # En caso de que no haya cobros, devolver 0

    cursor.close()

    # Preparar los datos como un objeto JSON
    data = {
        'cantidad_patentes': cantidad_patentes,
        'cantidad_ubicaciones': cantidad_ubicaciones,
        'suma_cobros': suma_cobros
    }

    return (data)

