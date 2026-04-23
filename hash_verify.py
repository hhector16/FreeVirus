import hashlib
from time import strftime
import hash_cache
import requests
import time
import json
import verifyNumberOfEx
import entropy_verify



API_KEY = "b76a6aef7a2aaf60aedcdd3d6bc4f7d656c593c103b12f3b85bcb1fcb8ba11cc"
HEADERS = {
    "x-apikey": API_KEY
}

min_malware_score = 50
min_suspicious_score = 20

'''
EJEMPLO DE ESTRUCTURA DE LA RESPUESTA
{
  "data": {
    "attributes": {
      "last_analysis_stats": {
        "malicious": 1,
        "suspicious": 3,
        "undetected": 58,
        "harmless": 4,
        "timeout": 0
      }
    }
  }
}
'''

def load_json():
    try:
        with open("conf.json","r") as f:
            data = json.load(f)
            min_malware_score = data["min_malware_score"]
            min_suspicious_score = data["min_suspicious_score"]
    except:
        print("Ha ocurrido un error con el JSON jajaja ci")
        min_malware_score = 50
        min_suspicious_score = 20


def hash_file_with_path(path):
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return None

def whitelist(path):
        if(path.startswith(("/usr/lib/x86_64-linux-gnu/", "/usr/bin/git" , "usr/bin/bash" ,"/bin/","/lib/","/sbin/","/lib64/","/proc/","/sys/","/dev/","/run/","/update-motd.d/")) ):
            return True
def verify_sha256(x, pid, ppid,event):
    load_json()
    score = 0
    if event & 0x00000020:
        event_name = "EXEC"
    elif event & 0x00000008:
        event_name = "DOWNLOAD"
    else:
        event_name = "OTHER"
    
    hash = hash_file_with_path(x)

    if(whitelist(x)):
        return 0
    else:
        if hash_cache.contains_hash(hash):
            # new instance
            hash_cache.store_instance(hash,pid,ppid,x,event_name)
            #verifyNumberOfEx.decay_score(hash)
            hash_cache.update_last_seen(hash,time.time())
            #verifyNumberOfEx.execution_check(hash)
            print("YA EXISTIA")
            return hash
        else:

            if (x.startswith("/tmp") or x.startswith("/var/tmp" or x.startswith("/dev/shm"))):
                score += 10
            
            url = f"https://www.virustotal.com/api/v3/files/{hash}"
            
            try:
                r = requests.get(url, headers=HEADERS, timeout=10)
                
                
                if (r.status_code == 404):    # No se sabe de este archivo, se suma puntos de sospechoso
                    print("Archivo no encontrado en VirusTotal, asignando puntuación de sospechoso")
                    score = 20
                    state = 1  # unknown
                    hash_cache.store_hash(hash,score,state)
                elif(r.status_code != 200):
                    print("Error al conectar con VirusTotal:", r.status_code)
                    return None
                    
                data = r.json()
                
                stats = data["data"]["attributes"]["last_analysis_stats"]
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)

                # Calcular score simple
                score += malicious * 10 + suspicious * 5

                # Now we calculate the entropy

                entropy = entropy_verify.entropy_check(x)

                print("****", entropy)  

                score += entropy


                # Decidir veredicto
                if score >= min_malware_score:
                    state = 2
                elif score >= min_suspicious_score:
                    state = 1
                else:
                    state = 0
                
                hash_cache.store_hash(hash,score,state)
                hash_cache.store_instance(hash,pid,ppid,x,event_name)
                score = hash_cache.get_score(hash)
                state = hash_cache.get_state(hash)
                print(hash)
                return hash
            except Exception as e:
                print("Excepción al conectar con VirusTotal:", str(e))
                return "ERROR "