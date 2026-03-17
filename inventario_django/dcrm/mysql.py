import mysql.connector
dataBase = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "")
 
# Se crrea un cursor para recorrer las filas y las columnas de la base de datos
cursorObject = dataBase.cursor()#Se creea un cursor para ejecutar comandos SQL
cursorObject.execute("CREATE DATABASE cliente")#Se ejecuta el comando SQL para crear la base de datos llamada "cliente"
print("Base de datos creada con exito")#Se imprime un mensaje de confimacion