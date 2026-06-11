# 02 — Stack tecnológico

## Resumen

| Capa | Tecnología | Rol |
|---|---|---|
| Chat + RAG | Open WebUI (Docker, imagen oficial) | UI de chat, Knowledge Bases, embeddings, RAG |
| Modelos | OpenRouter (API OpenAI-compatible) | Acceso multi-modelo con una key |
| Notas | Markdown + frontmatter YAML, repo Git (GitHub privado) | Fuente de verdad |
| Sync | Python 3.11+, `requests`, `pyyaml` | Repo → Knowledge Bases vía API de Open WebUI |
| Captura | FastAPI + página HTML simple (y/o bot de Telegram) | Entrada rápida + clasificador LLM |
| Reverse proxy | Caddy | HTTPS automático, dominios para webui y capture |
| Orquestación | Docker Compose | Todo el VPS en un solo archivo |
| VPS | Hetzner / DigitalOcean / similar, 2 GB RAM mínimo | Hosting |
| Gestión Python | `uv` | Dependencias y entornos |
| Calidad | `ruff` (lint + format), `pytest` para el clasificador | Verificación |

## Notas por componente

### Open WebUI
- Imagen: `ghcr.io/open-webui/open-webui:main`.
- Variables clave: `OPENAI_API_BASE_URL=https://openrouter.ai/api/v1`, `OPENAI_API_KEY=<key de OpenRouter>`, `ENABLE_SIGNUP=false` tras crear la cuenta admin.
- El RAG (motor de embeddings, chunking, vector store) viene incluido; usar configuración por defecto al inicio y ajustar solo si la calidad de búsqueda lo pide.
- API REST documentada para gestionar Knowledge Bases y archivos (usar API key generada desde Settings → Account).
- **El agente debe verificar la documentación actual de Open WebUI antes de implementar la integración con su API**, porque el proyecto evoluciona rápido: https://docs.openwebui.com

### OpenRouter
- Endpoint OpenAI-compatible: `https://openrouter.ai/api/v1/chat/completions`.
- Para el clasificador usar un modelo barato y rápido (definirlo en `.env`, p. ej. una variable `CLASSIFIER_MODEL`). El usuario elegirá el modelo concreto; sugerir 2-3 opciones económicas vigentes al momento de implementar.

### Estructura del repo (monorepo)
Un solo repo contiene el vault y el código. Razón: simplicidad para un proyecto personal; el sync y capture viven junto a los datos que manejan. Si el vault crece mucho, separar después es trivial.

### VPS
- Requisito mínimo: 2 GB RAM (Open WebUI + embeddings locales lo necesitan). 
- Instalación base: Docker + Docker Compose, firewall (solo 80/443/SSH), usuario no-root.
- Dominio o subdominio apuntando al VPS (puede ser un dominio barato o DuckDNS para empezar).

## Variables de entorno (`.env.example`)

```env
# OpenRouter
OPENROUTER_API_KEY=
CLASSIFIER_MODEL=          # modelo barato para clasificar capturas

# Open WebUI
WEBUI_URL=https://chat.tudominio.com
WEBUI_API_KEY=             # generada en Open WebUI tras instalar

# Capture
CAPTURE_TOKEN=             # token simple para proteger la app de captura
TELEGRAM_BOT_TOKEN=        # opcional, solo si se usa bot

# Git
VAULT_REPO_URL=            # repo del vault (SSH)
GIT_AUTHOR_NAME=
GIT_AUTHOR_EMAIL=
```
