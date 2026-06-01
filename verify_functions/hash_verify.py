import hashlib
from time import strftime
import databases.hash_cache as hash_cache
import requests
import time
import json
from verify_functions import entropy_verify
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

min_suspicious_score = 30
min_malware_score = 50

API_KEY = os.getenv("API_KEY")
HEADERS = {
    "x-apikey": API_KEY
}


'''
RESPONSE EXAMPLE
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

# Function which gets the value of the json file
def load_json():
    try:
        with open("conf.json","r") as f:
            data = json.load(f)
            min_malware_score = data["min_malware_score"]
            min_suspicious_score = data["min_suspicious_score"]
    except:
        print("Error json")
        min_malware_score = 50
        min_suspicious_score = 20

# Function that obtains the hash
def hash_file_with_path(path):
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return None

# Decides which files shouldnt be analized
def whitelist(path):
        if(path.startswith(("/usr/lib/x86_64-linux-gnu/", "/usr/bin/git" , "usr/bin/bash" ,"/bin/","/lib/","/sbin/","/lib64/","/proc/","/sys/","/dev/","/run/","/update-motd.d/")) ):
            return True

# Main function. Gets file and analizes it thanks tu VirusTotal. Then it checks if its already in the hashes database
# If its not, the API call is done and also its verified its entropy, where the file is executed or downloaded...
# If it exists then an instance is created and stored in the instance database
# Every file is registered with the pid, ppid and dates so we can have a better feedback
def verify_sha256(x, pid, ppid,event):
    load_json()
    score = 0
    if (event & 0x00000008) != 0:
        event_name = "DOWNLOAD"
    else:
        event_name = "EXEC"
    
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
                
                
                if (r.status_code == 404):    
                    print("File not found. Setting default score")
                    score = 20
                    state = 1  # unknown
                    hash_cache.store_hash(hash,score,state)
                elif(r.status_code != 200):
                    print("Error trying to connect with VirusTotal:", r.status_code)
                    return None
                    
                data = r.json()
                
                stats = data["data"]["attributes"]["last_analysis_stats"]
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)

                # Caculate score
                score += malicious * 10 + suspicious * 5

                # Now we calculate the entropy

                entropy = entropy_verify.entropy_check(x)


                score += entropy


                # Decision making
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
                return hash
            except Exception as e:
                print("Exception :", str(e))
                return "ERROR "