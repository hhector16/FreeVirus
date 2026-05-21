import sqlite3

def consulta(hash):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM hashes WHERE hash = ?",(hash,))
    result = cursor.fetchall()

    print(result)
    conexion.close()

consulta("19dd65dde495c4dc2193cf944f4afce164262ac885edb09d2fbce0739a9d30ef")