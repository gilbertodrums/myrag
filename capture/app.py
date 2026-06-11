import os
import datetime
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv

from .classifier import classify_text, get_available_folders

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
CAPTURE_TOKEN = os.getenv("CAPTURE_TOKEN")

app = FastAPI(title="MyRAG Capture App")

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
WORKSPACE_ROOT = Path(__file__).parent.parent

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

def verify_token(token: Optional[str] = None):
    if token != CAPTURE_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, t: Optional[str] = None):
    if t != CAPTURE_TOKEN:
        return HTMLResponse("<h1>401 No Autorizado</h1>", status_code=401)
    
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "token": t, "folders": get_available_folders()}
    )

@app.post("/capture")
async def capture(req: CaptureRequest, token: str):
    verify_token(token)
    classification = classify_text(req.text)
    return classification

@app.post("/save")
async def save(req: SaveRequest, token: str):
    verify_token(token)
    
    # Crear slug del título
    slug = "".join([c if c.isalnum() else "-" for c in req.title.lower()])
    import re
    slug = re.sub(r'-+', '-', slug).strip('-')
    if not slug:
        slug = f"nota-{int(datetime.datetime.now().timestamp())}"
        
    folder = req.project
    if folder not in get_available_folders():
        folder = "inbox"
        
    filename = f"{slug}.md"
    filepath = WORKSPACE_ROOT / "vault" / folder / filename
    
    # Prevenir sobreescritura
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

    # Git operations
    try:
        subprocess.run(["git", "add", str(filepath)], cwd=WORKSPACE_ROOT, check=True)
        subprocess.run(["git", "commit", "-m", f"feat(vault): captura '{req.title}'"], cwd=WORKSPACE_ROOT, check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=WORKSPACE_ROOT, check=True)
        git_status = "ok"
    except subprocess.CalledProcessError as e:
        git_status = f"error: {e}"

    return {"status": "ok", "path": f"vault/{folder}/{filepath.name}", "git": git_status}
