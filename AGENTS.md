# AGENTS.md — Arnés del agente para el proyecto "Knowledge Hub"

> Este archivo sigue el estándar abierto AGENTS.md. Es la fuente de verdad para cualquier
> agente de IA (Claude Code, Cursor, Codex, etc.) que trabaje en este proyecto.
> Léelo completo antes de escribir una sola línea de código.

## Qué es este proyecto

Un sistema personal de gestión de conocimiento ("second brain") con chat de IA:

1. Las notas del usuario viven como archivos **Markdown con frontmatter YAML** en este repo de GitHub, organizadas por carpetas/proyectos.
2. **Open WebUI** (self-hosteado en un VPS con Docker) provee el chat con RAG sobre esas notas, conectado a **OpenRouter** (multi-modelo).
3. Una **app de captura rápida** permite pegar texto desde cualquier lugar; un LLM clasificador lo convierte en nota Markdown, le asigna proyecto, título y tags, y lo commitea al repo.
4. Un **script de sincronización** sube las notas del repo a las Knowledge Bases de Open WebUI vía su API.

Lee la visión completa en `docs/00-vision.md` y la arquitectura en `docs/01-arquitectura.md` antes de empezar cualquier tarea.

## Orden de trabajo

El proyecto se construye por fases. **No avances a una fase sin completar y verificar la anterior.**

1. `tasks/fase-1-infraestructura.md` — VPS + Open WebUI + OpenRouter funcionando.
2. `tasks/fase-2-sync.md` — Estructura de notas + script de sincronización repo → Open WebUI.
3. `tasks/fase-3-captura.md` — App de captura rápida con clasificador LLM.
4. `tasks/fase-4-dashboard.md` — (Opcional, futuro) Vista web interactiva propia.

Cada archivo de tarea tiene criterios de aceptación explícitos. Una tarea está terminada **solo** cuando todos sus criterios se cumplen y lo has verificado ejecutando los comandos de verificación indicados.

## Reglas del proyecto (no negociables)

- **Secretos:** NUNCA escribas API keys, tokens o contraseñas en código, commits o archivos del repo. Todo secreto va en variables de entorno (`.env`, que está en `.gitignore`). Si necesitas un secreto que no existe, detente y pídeselo al usuario.
- **Datos del usuario:** las notas en `vault/` son datos personales. No las borres, sobrescribas ni reformatees masivamente sin confirmación explícita del usuario. Las operaciones destructivas requieren confirmación.
- **Portabilidad primero:** las notas deben ser siempre Markdown plano legible por humanos. Ninguna decisión técnica puede atar los datos a una plataforma (ni a Open WebUI, ni a una base de datos propietaria). Open WebUI es reemplazable; el repo de notas es lo permanente.
- **Simplicidad:** prefiere la solución más simple que cumpla los criterios de aceptación. No agregues frameworks, abstracciones ni features no pedidos. El usuario construye con vibe coding: el código debe ser legible y fácil de modificar.
- **Idioma:** el código y nombres de variables en inglés; comentarios, documentación y mensajes al usuario en español.

## Stack y convenciones

- **Backend/scripts:** Python 3.11+ con `uv` como gestor de paquetes. Tipado con type hints. Formateo con `ruff`.
- **App de captura:** FastAPI + HTML/JS simple (sin framework pesado) o, si el usuario lo prefiere, un bot de Telegram con `python-telegram-bot`.
- **Infra:** Docker Compose para todo lo que corre en el VPS. Un solo `docker-compose.yml` en la raíz de `infra/`.
- **LLM:** todas las llamadas a modelos pasan por OpenRouter (`https://openrouter.ai/api/v1`, API compatible con OpenAI). El modelo se define en variable de entorno, nunca hardcodeado.
- **Commits:** mensajes en formato convencional (`feat:`, `fix:`, `docs:`, `chore:`), pequeños y atómicos.

Detalles completos del stack y por qué se eligió cada pieza: `docs/02-stack.md`.

## Formato de las notas

Toda nota generada o tocada por el sistema debe cumplir el esquema de frontmatter definido en `docs/03-estructura-datos.md`. Resumen mínimo:

```markdown
---
title: "Título descriptivo"
type: prompt | recurso | nota | snippet | articulo
project: nombre-del-proyecto
tags: [tag1, tag2]
source: "URL o 'manual'"
created: 2026-06-10
---

Contenido en markdown...
```

## Cómo verificar tu trabajo

- Después de cada cambio de código: ejecuta `ruff check .` y los tests si existen (`uv run pytest`).
- Después de cambios de infra: `docker compose config` para validar sintaxis y luego levanta y prueba el servicio.
- Cada tarea define sus propios comandos de verificación; ejecútalos antes de dar la tarea por cerrada.
- Si algo falla más de 2 veces con el mismo enfoque, detente, explica el problema al usuario y propón alternativas en lugar de insistir.

## Qué hacer ante ambigüedad

- Si una decisión afecta los datos del usuario, el costo del VPS, o la estructura del repo → pregunta antes.
- Si es un detalle de implementación menor → decide tú, documenta la decisión en el código y continúa.
- Si los docs se contradicen entre sí → `AGENTS.md` manda, luego `docs/01-arquitectura.md`, y avisa al usuario de la contradicción para corregirla.

## Estructura esperada del repo al finalizar

```
knowledge-hub/
├── AGENTS.md
├── README.md
├── .env.example          # plantilla de secretos (sin valores reales)
├── .gitignore
├── docs/                 # diseño y decisiones
├── tasks/                # tareas por fase con criterios de aceptación
├── vault/                # LAS NOTAS DEL USUARIO (markdown)
│   ├── prompts/
│   ├── mcp/
│   ├── recursos/
│   └── proyectos/<nombre>/
├── sync/                 # script de sincronización repo → Open WebUI
├── capture/              # app de captura rápida + clasificador
└── infra/                # docker-compose.yml y configuración del VPS
```
