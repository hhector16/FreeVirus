import hash_cache
import sqlite3
conn = sqlite3.connect("hashes.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM hashes")
print(cursor.fetchall())