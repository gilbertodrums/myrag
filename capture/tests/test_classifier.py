import json
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from classifier import classify_text

def test_classify_text_success():
    mock_response = {
        "title": "Un Prompt Genial",
        "type": "prompt",
        "project": "prompts",
        "tags": ["test"],
        "summary": "Resumen corto.",
        "confidence": 0.9
    }
    
    with patch("requests.post") as mock_post:
        # Mockear la respuesta de la API de OpenRouter
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": json.dumps(mock_response)}}]
        }
        mock_post.return_value.raise_for_status.return_value = None
        
        # Test
        res = classify_text("Actúa como un experto en testing")
        
        assert res["title"] == "Un Prompt Genial"
        assert res["project"] == "prompts"
        assert res["type"] == "prompt"
        assert res["confidence"] == 0.9

def test_classify_text_low_confidence():
    mock_response = {
        "title": "Algo ambiguo",
        "type": "nota",
        "project": "prompts", # Project incorrecto dado la baja confianza
        "tags": ["test"],
        "summary": "Resumen corto.",
        "confidence": 0.3 # Baja confianza -> debería ir a inbox
    }
    
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": json.dumps(mock_response)}}]
        }
        
        res = classify_text("hola")
        
        assert res["project"] == "inbox" # Redirigido a inbox automáticamente

def test_classify_text_fallback_on_error():
    with patch("requests.post") as mock_post:
        # Forzar un error JSON
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "Esto no es JSON válido"}}]
        }
        
        res = classify_text("Prueba de error")
        
        assert res["project"] == "inbox"
        assert res["type"] == "nota"
        assert res["confidence"] == 0.0
        assert "Prueba de error" in res["title"]
