import os
import json
import hashlib
import logging
from pathlib import Path

import yaml
import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
API_KEY = os.getenv("OPEN_WEBUI_API_KEY")
BASE_URL = "http://localhost:3000/api/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

STATE_FILE = Path(__file__).parent / ".state.json"
CONFIG_FILE = Path(__file__).parent / "config.yaml"
WORKSPACE_ROOT = Path(__file__).parent.parent

def calculate_hash(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_kbs():
    res = requests.get(f"{BASE_URL}/knowledge/", headers=HEADERS)
    res.raise_for_status()
    return res.json().get("items", [])

def create_kb(name: str) -> str:
    res = requests.post(f"{BASE_URL}/knowledge/create", headers=HEADERS, json={"name": name, "description": ""})
    res.raise_for_status()
    data = res.json()
    return data["id"]

def upload_file(filepath: Path) -> str:
    with open(filepath, "rb") as f:
        files = {"file": (filepath.name, f, "text/markdown")}
        res = requests.post(f"{BASE_URL}/files/", headers=HEADERS, files=files)
        res.raise_for_status()
        return res.json()["id"]

def delete_file(file_id: str):
    try:
        requests.delete(f"{BASE_URL}/files/{file_id}", headers=HEADERS)
    except Exception as e:
        logging.warning(f"No se pudo eliminar el archivo {file_id}: {e}")

def add_file_to_kb(kb_id: str, file_id: str):
    res = requests.post(
        f"{BASE_URL}/knowledge/{kb_id}/file/add",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"file_id": file_id}
    )
    res.raise_for_status()

def main():
    if not API_KEY:
        logging.error("No se encontró OPEN_WEBUI_API_KEY en .env")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
    else:
        state = {}

    logging.info("Conectando con Open WebUI y resolviendo Knowledge Bases...")
    existing_kbs = {kb["name"]: kb["id"] for kb in get_kbs()}
    
    # Resolver KBs de configuración
    kb_mapping = {} # kb_name -> kb_id
    path_to_kbs = {} # folder_path -> list of kb_names

    for kb_conf in config.get("knowledge_bases", []):
        name = kb_conf["name"]
        if name not in existing_kbs:
            logging.info(f"Creando Knowledge Base: '{name}'")
            kb_id = create_kb(name)
            existing_kbs[name] = kb_id
        else:
            kb_id = existing_kbs[name]
        
        kb_mapping[name] = kb_id
        for p in kb_conf.get("paths", []):
            path_to_kbs.setdefault(p, []).append(name)

    # Identificar todos los archivos .md en el workspace
    current_files = {} # rel_path -> hash
    md_files = list(WORKSPACE_ROOT.glob("vault/**/*.md"))
    
    for f in md_files:
        rel_path = f.relative_to(WORKSPACE_ROOT).as_posix()
        current_files[rel_path] = calculate_hash(f)

    cambios = 0

    # Determinar archivos a eliminar (ya no existen)
    archivos_a_eliminar = [p for p in state if p not in current_files]
    for p in archivos_a_eliminar:
        logging.info(f"Archivo eliminado: {p}")
        file_id = state[p].get("file_id")
        if file_id:
            delete_file(file_id)
        del state[p]
        cambios += 1

    # Procesar archivos actuales
    for rel_path, file_hash in current_files.items():
        is_new = rel_path not in state
        is_modified = not is_new and state[rel_path]["hash"] != file_hash

        if is_new or is_modified:
            if is_modified:
                logging.info(f"Modificado: {rel_path}")
                # Borrar el archivo viejo de Open WebUI (esto lo quita de las KBs también)
                old_file_id = state[rel_path].get("file_id")
                if old_file_id:
                    delete_file(old_file_id)
            else:
                logging.info(f"Nuevo: {rel_path}")

            # Subir el nuevo archivo
            filepath = WORKSPACE_ROOT / rel_path
            try:
                new_file_id = upload_file(filepath)
                
                # Asignarlo a las KBs que correspondan
                target_kbs = set()
                # Un archivo pertenece a una KB si su ruta empieza con alguno de los paths mapeados a esa KB
                for configured_path, kbs in path_to_kbs.items():
                    # Si el archivo está dentro del configured_path
                    # Por ejemplo, configured_path "vault/prompts/", rel_path "vault/prompts/resumir.md"
                    if rel_path.startswith(configured_path) or (configured_path == "vault/" and rel_path.startswith("vault/")):
                        target_kbs.update(kbs)
                
                for kb_name in target_kbs:
                    kb_id = kb_mapping[kb_name]
                    add_file_to_kb(kb_id, new_file_id)
                    logging.info(f"  -> Añadido a KB '{kb_name}'")

                # Actualizar estado local
                state[rel_path] = {"hash": file_hash, "file_id": new_file_id}
                cambios += 1

            except Exception as e:
                logging.error(f"Error procesando {rel_path}: {e}")

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    if cambios == 0:
        logging.info("0 cambios. El vault está sincronizado.")
    else:
        logging.info(f"Sincronización completada. {cambios} cambios aplicados.")

if __name__ == "__main__":
    main()
