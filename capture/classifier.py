import os
import json
import logging
from pathlib import Path
from typing import List, Literal

import requests
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", "google/gemini-2.5-flash")

WORKSPACE_ROOT = Path(__file__).parent.parent
PROMPT_FILE = Path(__file__).parent / "classifier_prompt.md"

class ClassificationResult(BaseModel):
    title: str
    type: Literal["prompt", "recurso", "nota", "snippet", "articulo"]
    project: str
    tags: List[str]
    summary: str
    confidence: float

def get_available_folders() -> List[str]:
    vault_dir = WORKSPACE_ROOT / "vault"
    if not vault_dir.exists():
        return ["inbox"]
    return [d.name for d in vault_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

def build_system_prompt() -> str:
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    
    folders = get_available_folders()
    folders_str = ", ".join([f'"{f}"' for f in folders])
    return prompt_template.replace("{available_folders}", folders_str)

def classify_text(text: str) -> dict:
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY no está configurada")

    system_prompt = build_system_prompt()
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": CLASSIFIER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Texto a clasificar:\n\n{text}"}
        ],
        "response_format": {"type": "json_object"}
    }
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            res.raise_for_status()
            
            data = res.json()
            content = data["choices"][0]["message"]["content"]
            
            # Limpiar contenido si viene con markdown
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
            content = content.strip()
            
            parsed_json = json.loads(content)
            
            # Validar con Pydantic
            validated = ClassificationResult(**parsed_json)
            
            # Si confidence < 0.6 o la carpeta no existe, mandar a inbox
            final_dict = validated.model_dump()
            valid_folders = get_available_folders()
            
            if final_dict["confidence"] < 0.6 or final_dict["project"] not in valid_folders:
                final_dict["project"] = "inbox"
                
            return final_dict
            
        except (ValidationError, json.JSONDecodeError) as e:
            logging.warning(f"Error parseando JSON (intento {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                # Falla tras reintentos, fallback
                return fallback_classification(text)
        except Exception as e:
            logging.error(f"Error llamando a OpenRouter: {e}")
            return fallback_classification(text)

def fallback_classification(text: str) -> dict:
    return {
        "title": "Nota sin clasificar " + text[:20].replace('\n', ' '),
        "type": "nota",
        "project": "inbox",
        "tags": ["inbox", "auto"],
        "summary": "Falló la clasificación automática.",
        "confidence": 0.0
    }
