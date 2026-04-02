import sqlite3

# Conectar a la base de datos (asegúrate de poner la ruta correcta a tu archivo .db)
conn = sqlite3.connect('hashes.db')

# Crear un cursor para interactuar con la base de datos
cursor = conn.cursor()

# Realizar una consulta SQL para obtener todas las filas de una tabla
cursor.execute("SELECT * FROM hashes")  # Cambia 'mi_tabla' por el nombre de tu tabla

# Obtener todas las filas de la consulta
rows = cursor.fetchall()

# Imprimir las filas obtenidas
for row in rows:
    print(row)

# Cerrar la conexión
conn.close()