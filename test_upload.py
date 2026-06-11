import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPEN_WEBUI_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

# Crear un archivo markdown de prueba
with open("test.md", "w") as f:
    f.write("# Hello\nThis is a test.")

# 1. Subir archivo a /api/v1/files/
print("Uploading file...")
with open("test.md", "rb") as f:
    files = {"file": ("test.md", f, "text/markdown")}
    res = requests.post("http://localhost:3000/api/v1/files/", headers=headers, files=files)
    
if res.status_code == 200:
    file_data = res.json()
    print("File uploaded:", file_data)
    file_id = file_data.get("id")
    
    # 2. Obtener KB de prueba
    kb_res = requests.get("http://localhost:3000/api/v1/knowledge/", headers=headers)
    kbs = kb_res.json().get("items", [])
    if kbs:
        kb_id = kbs[0]["id"]
        print(f"Adding file to KB {kb_id}")
        # 3. Add to KB
        add_res = requests.post(
            f"http://localhost:3000/api/v1/knowledge/{kb_id}/file/add",
            headers={**headers, "Content-Type": "application/json"},
            json={"file_id": file_id}
        )
        print("Add to KB status:", add_res.status_code)
        print(add_res.text)
else:
    print("Error uploading file:", res.status_code, res.text)
