import pymysql
from datetime import datetime

connection = pymysql.connect(
    host="localhost", 
    user="kbza",
    password="kbza52",
    db="registros_patentes"
)
fecha_hora_actual = datetime.now()

def 
cursor = connection.cursor()

sql= "INSERT INTO patentes(image,created,id_patente,ubicacion) VALUES ('0','hora_actual','0','0')"
    
cursor.execute(sql)
    
connection.commit()