import sqlite3
import hash_cache
import json
import time

def get_executed_time(hash):
    conn = sqlite3.connect("instances.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM instances WHERE hash = ? ORDER BY id DESC LIMIT 1", (hash,))
    #cursor.execute("SELECT * FROM instances WHERE hash = ?", (hash,))

    fecha = cursor.fetchone()[0]
    conn.close()
    return fecha

def get_executions_last_hour(hash):
    time = get_executed_time(hash)
    one_hour_ago = time - 3600

    conn = sqlite3.connect("instances.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM instances WHERE hash = ? AND timestamp > ?", (hash,one_hour_ago))
    #cursor.execute("SELECT * FROM instances WHERE hash = ?", (hash,))

    fecha = cursor.fetchall()
    print(fecha)
    number = len(fecha)
    print(number)
    conn.close()

    return number
    print(actual_score + number)

def execution_check(hash):
    actual_score = hash_cache.get_score(hash)[0]
    print("**************************")
    print(actual_score)
    print("**************************")

    number = get_executions_last_hour(hash)
    actualized_score = actual_score + number
    hash_cache.update_score(hash,actualized_score)

    with open("archivo.txt", "w", encoding="utf-8") as f:
        f.write("datoSs : " + str(actualized_score) + "actual : " + str(actual_score))

    try:
        with open("conf.json","r") as f:
            data = json.load(f)
        if (actualized_score < data["min_suspicious_score"]):
            hash_cache.update_state(hash,0)
        elif (actualized_score < data["min_suspicious_score"] and actualized_score > data["min_malware_score"]):
            hash_cache.update_state(hash,1)
        elif (actualized_score > data["min_malware_score"]):
            hash_cache.update_state(hash,2)

    except Exception as e:
        print("Error grave al acceder al json, ",e)
        print("TORTILLAAA")

def decay_score(hash):
    now = int(time.time())
    last_seen = hash_cache.get_last_seen(hash)[0]
    score = hash_cache.get_score(hash)[0]

    decay_time = now - last_seen

    decay_time = decay_time // 60

    new_score = max(0, score - decay_time)
    hash_cache.update_score(hash,new_score)
        
