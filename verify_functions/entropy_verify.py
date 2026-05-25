import math
from collections import Counter

def entropy_check(path):
    try:
        with open(path, "rb") as f:
            data = f.read()

        if not data:
            return 0.0

        counter = Counter(data)
        length = len(data)

        ent = 0.0
        for count in counter.values():
            p = count / length
            ent -= p * math.log2(p)
        print("Entropy = ",ent)
        return ent

    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return None