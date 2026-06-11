import os
import re
import sys
import datetime
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Añadir el directorio sync al path para poder importar sync.py
sys.path.insert(0, str(Path(__file__).parent.parent / "sync"))
import sync as syncer

from classifier import classify_text, get_available_folders

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
CAPTURE_TOKEN = os.getenv("CAPTURE_TOKEN")

app = FastAPI(title="MyRAG Capture App")

WORKSPACE_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = Path(__file__).parent / "templates"


class CaptureRequest(BaseModel):
    text: str


class SaveRequest(BaseModel):
    title: str
    type: str
    project: str
    tags: list[str]
    summary: str
    content: str
    source: str = "manual"


def verify_token(token: Optional[str]):
    if token != CAPTURE_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")


@app.get("/", response_class=HTMLResponse)
async def read_root(t: Optional[str] = None):
    if t != CAPTURE_TOKEN:
        return HTMLResponse("<h1>401 No Autorizado</h1>", status_code=401)
    return FileResponse(TEMPLATES_DIR / "index.html")


@app.get("/api/folders")
async def api_folders(t: Optional[str] = None):
    verify_token(t)
    return {"folders": get_available_folders()}


@app.post("/capture")
async def capture(req: CaptureRequest, token: str):
    verify_token(token)
    classification = classify_text(req.text)
    return classification


@app.post("/save")
async def save(req: SaveRequest, token: str):
    verify_token(token)

    slug = "".join([c if c.isalnum() else "-" for c in req.title.lower()])
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        slug = f"nota-{int(datetime.datetime.now().timestamp())}"

    folder = req.project
    if folder not in get_available_folders():
        folder = "inbox"

    filepath = WORKSPACE_ROOT / "vault" / folder / f"{slug}.md"

    counter = 1
    while filepath.exists():
        filepath = WORKSPACE_ROOT / "vault" / folder / f"{slug}-{counter}.md"
        counter += 1

    tags_str = ", ".join(req.tags)
    frontmatter = f"""---
title: "{req.title.replace('"', "'")}"
type: {req.type}
project: {folder}
tags: [{tags_str}]
source: "{req.source}"
created: {datetime.date.today().isoformat()}
summary: "{req.summary.replace('"', "'")}"
---

{req.content}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter)

    try:
        subprocess.run(["git", "add", str(filepath)], cwd=WORKSPACE_ROOT, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"feat(vault): captura '{req.title}'"],
            cwd=WORKSPACE_ROOT,
            check=True,
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=WORKSPACE_ROOT, check=True)
        git_status = "ok"
        # Sincronizar con Open WebUI en background automáticamente
        import threading
        threading.Thread(target=syncer.main, daemon=True).start()
    except subprocess.CalledProcessError as e:
        git_status = f"error: {e}"

    return {"status": "ok", "path": f"vault/{folder}/{filepath.name}", "git": git_status}


async def run_sync_background():
    """Corre el sync en un hilo separado para no bloquear la respuesta."""
    import threading
    t = threading.Thread(target=syncer.main, daemon=True)
    t.start()
