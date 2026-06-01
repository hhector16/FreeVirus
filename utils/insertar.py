import sqlite3
import os

# Ruta absoluta de hashes.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"databases", "hashes.db")


# LO RELACIONADO CON LA BASE DE DATOS DE HASHES

def init_hashes_db():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hashes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE NOT NULL,
        state INTEGER DEFAULT 0,
        score INTEGER DEFAULT 0,
        first_seen INTEGER DEFAULT (strftime('%s','now')),
        last_seen INTEGER DEFAULT (strftime('%s','now'))
    )
    """)

    conexion.commit()
    conexion.close()


def store_hash(hash, score, state):
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO hashes (hash,score,state) VALUES (19dd65dde495c4dc2193cf944f4afce164262ac885edb09d2fbce0739a9d30ef,10,0)",
        (hash, score, state)
    )

    conexion.commit()
    conexion.close()