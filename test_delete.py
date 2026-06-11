import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPEN_WEBUI_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

# Get files
res = requests.get("http://localhost:3000/api/v1/files/", headers=headers)
if res.status_code == 200:
    for f in res.json():
        file_id = f.get("id")
        print("Deleting", file_id)
        d_res = requests.delete(f"http://localhost:3000/api/v1/files/{file_id}", headers=headers)
        print("Status:", d_res.status_code)
else:
    print("Failed to get files", res.status_code)

# Check KB
kb_res = requests.get("http://localhost:3000/api/v1/knowledge/", headers=headers)
print("KBs:", kb_res.json())
