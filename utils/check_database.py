import sqlite3
import os

# Ruta absoluta de hashes.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"databases", "hashes.db")

def consulta(hash):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM hashes WHERE hash = ?",(hash,))
    result = cursor.fetchall()

    print(result)
    conexion.close()

consulta("19dd65dde495c4dc2193cf944f4afce164262ac885edb09d2fbce0739a9d30ef")