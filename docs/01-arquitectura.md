# 01 — Arquitectura

## Diagrama general

```
                    ┌─────────────────────────────────────────┐
                    │              VPS (~$5/mes)              │
                    │                                         │
  Navegador ──────► │  ┌──────────────┐   ┌────────────────┐  │
  (PC / móvil)      │  │  Open WebUI  │──►│   OpenRouter   │──► GPT / Claude /
                    │  │  chat + RAG  │   │ (API externa)  │    Gemini / etc.
                    │  └──────▲───────┘   └────────▲───────┘  │
                    │         │ API                │          │
                    │  ┌──────┴───────┐   ┌────────┴───────┐  │
  Pegar texto ────► │  │   Capture    │──►│  Clasificador  │  │
  (web o Telegram)  │  │   (FastAPI)  │   │  (LLM barato)  │  │
                    │  └──────┬───────┘   └────────────────┘  │
                    └─────────┼───────────────────────────────┘
                              │ git commit + push
                              ▼
                    ┌─────────────────────┐
                    │   GitHub: vault/    │ ◄── Obsidian (opcional,
                    │  notas en markdown  │     edición local + grafo)
                    └─────────┬───────────┘
                              │ sync (script, cron o GitHub Action)
                              ▼
                     Knowledge Bases de Open WebUI
```

## Componentes

### 1. Vault (el corazón)
Repo Git con las notas en Markdown + frontmatter YAML. Estructura por carpetas = proyectos. Es la única fuente de verdad. Todo lo demás se puede destruir y reconstruir desde aquí.

### 2. Open WebUI (chat + RAG) — *adoptado, no construido*
- Corre en Docker en el VPS, detrás de Caddy (HTTPS automático).
- Conectado a OpenRouter como proveedor OpenAI-compatible → acceso a decenas de modelos con una sola key.
- **Knowledge Bases:** una por área (prompts, mcp, recursos, y una por proyecto activo). El usuario asocia una KB a un chat y pregunta; Open WebUI hace el RAG (embeddings + búsqueda semántica) internamente.
- Permite adjuntar archivos sueltos a un chat puntual (requisito del usuario).
- Tiene login propio → seguro para exponer a internet.

### 3. Sync (repo → Open WebUI) — *script propio, pequeño*
- Script Python que recorre `vault/`, detecta archivos nuevos/modificados/borrados (por hash) y los sube/actualiza/elimina en la Knowledge Base correcta vía la API REST de Open WebUI.
- Mapeo carpeta → Knowledge Base definido en un `sync/config.yaml`.
- Se ejecuta por cron en el VPS (cada 15 min) o como GitHub Action en cada push.

### 4. Capture (captura rápida + clasificador) — *app propia, el diferenciador*
- Página web mínima (un textarea + botón) protegida con un token simple, y/o bot de Telegram.
- Flujo: usuario pega texto → FastAPI lo envía a un LLM barato vía OpenRouter con un **prompt clasificador** → el LLM devuelve JSON (`title`, `type`, `project`, `tags`, `summary`) → la app genera el archivo `.md` con frontmatter, lo guarda en la carpeta correcta de `vault/` y hace commit + push.
- El usuario ve la clasificación propuesta y puede corregirla antes de guardar (o activar modo "confía y guarda").
- **Las reglas de clasificación viven en un prompt editable** (`capture/classifier_prompt.md`): así el usuario "le indica a la IA cómo ordenar su información" sin tocar código.

### 5. Obsidian (opcional)
Como el vault es un repo de markdown, el usuario puede clonarlo y abrirlo con Obsidian en PC para edición cómoda, vista de grafo y backlinks. Cero integración necesaria: es solo Git.

## Flujo de datos típico

1. Usuario encuentra un prompt interesante → lo pega en Capture.
2. Clasificador: `{type: "prompt", project: "prompts", tags: ["mcp", "diseño"], title: "Prompt para diseñar servidores MCP"}`.
3. Se crea `vault/prompts/prompt-para-disenar-servidores-mcp.md` y se pushea.
4. Sync lo sube a la KB "Prompts" de Open WebUI.
5. Días después, el usuario abre un chat con la KB "Prompts" y pregunta: *"¿tengo algo para diseñar un MCP?"* → el RAG encuentra la nota y el modelo responde citándola.

## Decisiones clave y alternativas descartadas

| Decisión | Alternativa descartada | Por qué |
|---|---|---|
| Open WebUI | Construir chat propio | RAG, multi-modelo, auth y UI ya resueltos y mantenidos |
| Markdown en Git | Base de datos / Notion | Portabilidad total, versionado gratis, compatible con Obsidian |
| OpenRouter | Keys directas por proveedor | Una sola key, cambio de modelo instantáneo (keys directas siguen siendo posibles en Open WebUI) |
| VPS propio | SaaS | Privacidad, costo fijo, control |
| Clasificación por LLM con prompt editable | Reglas hardcodeadas | El usuario ajusta el criterio en lenguaje natural |

## Seguridad

- Open WebUI con registro cerrado (solo la cuenta del usuario).
- Capture protegida por token en header/URL.
- HTTPS vía Caddy con certificado automático.
- Secretos solo en `.env` del VPS; el repo solo contiene `.env.example`.
- El repo del vault puede ser privado en GitHub.
