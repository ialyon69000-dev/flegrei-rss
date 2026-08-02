import requests
import json

url = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/events.json"

r = requests.get(url, timeout=30)
r.raise_for_status()

data = r.json()

print(type(data))

if isinstance(data, list):
    print("Nombre d'éléments :", len(data))
    print(json.dumps(data[0], indent=2, ensure_ascii=False))

elif isinstance(data, dict):
    print(data.keys())
    print(json.dumps(data, indent=2, ensure_ascii=False)[:5000])
