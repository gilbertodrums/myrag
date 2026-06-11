import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPEN_WEBUI_API_KEY")

def create_kb(name):
    url = "http://localhost:3000/api/v1/knowledge/create"
    data = json.dumps({"name": name, "description": ""}).encode('utf-8')
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as response:
            print(f"[{response.status}] Created KB")
            print(json.loads(response.read().decode()))
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] Error creating KB")
        print(e.read().decode())

def get_kbs():
    url = "http://localhost:3000/api/v1/knowledge/"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    try:
        with urllib.request.urlopen(req) as response:
            print(f"[{response.status}] GET KBs")
            print(json.dumps(json.loads(response.read().decode()), indent=2))
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] Error getting KBs")
        print(e.read().decode())

create_kb("Prueba")
get_kbs()
