import sqlite3


# LO RELACIONADO CON LA BASE DE DATOS DE HASHES

def init_hashes_db():
    conexion = sqlite3.connect("hashes.db")
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

def store_hash(hash,score,state):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("INSERT OR IGNORE INTO hashes (hash,score,state) VALUES (?,?,?)", (hash,score,state))
    conexion.commit()
    conexion.close()
    
def consult_hash(hash):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM hashes WHERE hash = ?", (hash,))
    result = cursor.fetchone()

    conexion.close()
    return result

def contains_hash(hash):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM hashes WHERE hash = ?", (hash,))
    result = cursor.fetchone()

    conexion.close()
    return result!= None
    
def update_hash(hash,state,score,last_seen):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("UPDATE hashes SET state = ?, score = ?, last_seen = ? WHERE hash = ?", (state, score, last_seen, hash))
    
    conexion.commit()
    conexion.close()
    
def delete_hash(hash):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM hashes WHERE hash = ?", (hash,))

    conexion.commit()
    conexion.close()
    
def update_last_seen(hash,last_seen):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("UPDATE hashes SET last_seen = ? WHERE hash = ?", (last_seen, hash))
    
    conexion.commit()
    conexion.close()

def update_score(hash,score):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("UPDATE hashes SET score = ? WHERE hash = ?", (score, hash))
    
    conexion.commit()
    conexion.close()

def get_score(hash):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT score FROM hashes WHERE hash = ?", (hash,))
    result = cursor.fetchone()
    conexion.close()
    return result

def update_state(hash,state):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("UPDATE hashes SET state = ? WHERE hash = ?", (state, hash))
    
    conexion.commit()
    conexion.close()

def get_state(hash):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT state FROM hashes WHERE hash = ?", (hash,))
    result = cursor.fetchone()
    conexion.close()
    return result

def get_last_seen(hash):
    conexion = sqlite3.connect("hashes.db")
    cursor = conexion.cursor()

    cursor.execute("SELECT last_seen FROM hashes WHERE hash = ?",(hash,))
    result = cursor.fetchone()
    conexion.close()
    return result

# BASE DE DATOS DE INSTANCIAS

def init_instances_db():
    conexion = sqlite3.connect("instances.db")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hash TEXT NOT NULL,
            timestamp INTEGER DEFAULT (strftime('%s','now')),
            pid INTEGER,
            ppid INTEGER,
            path TEXT,
            event TEXT, 
            FOREIGN KEY(hash) REFERENCES hashes(hash)
        );
        """)
    conexion.commit()
    conexion.close()
    
def store_instance(hash,pid,ppid,path,event):
    conexion = sqlite3.connect("instances.db")
    cursor = conexion.cursor()

    cursor.execute("INSERT INTO instances (hash,pid,ppid,path,event) VALUES (?,?,?,?,?)", (hash,pid,ppid,path,event))
    conexion.commit()
    conexion.close()