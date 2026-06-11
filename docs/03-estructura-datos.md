# 03 — Estructura de datos: el vault

## Estructura de carpetas

```
vault/
├── prompts/            # prompts que el usuario colecciona
├── mcp/                # recursos, configs y aprendizajes sobre MCP
├── skills/             # skills para modelos/agentes
├── recursos/           # artículos, herramientas, lanzamientos de IA
├── proyectos/
│   ├── <proyecto-a>/   # notas específicas de un proyecto
│   └── <proyecto-b>/
└── inbox/              # capturas sin clasificar (cuando el clasificador duda)
```

Reglas:
- Nombres de carpeta y archivo en `kebab-case`, sin espacios ni acentos.
- El clasificador solo puede crear archivos dentro de carpetas existentes; si no encaja en ninguna, va a `inbox/` para revisión manual.
- Crear nuevas carpetas de proyecto es decisión del usuario, nunca del clasificador.

## Esquema de frontmatter (obligatorio en toda nota)

```yaml
---
title: "Prompt para diseñar servidores MCP"   # string, descriptivo, max ~80 chars
type: prompt        # uno de: prompt | recurso | nota | snippet | articulo
project: prompts    # carpeta donde vive (relativa a vault/)
tags: [mcp, diseño, agentes]   # 2-5 tags en minúsculas, kebab-case
source: "https://ejemplo.com/post"   # URL de origen, o "manual"
created: 2026-06-10   # fecha ISO
summary: "Prompt estructurado en XML para guiar el diseño de un MCP server."  # 1-2 frases
---
```

Después del frontmatter, el contenido original en markdown, sin modificar (el clasificador NO reescribe el contenido del usuario; solo añade metadatos).

## Convenciones de contenido

- **Prompts:** el prompt va dentro de un bloque de código para copiarlo limpio. Si el usuario añadió contexto ("este prompt sirve para..."), va antes del bloque.
- **Recursos/artículos:** incluir siempre la URL en `source`. Si es un extracto largo de un artículo, el `summary` es clave para el RAG.
- **Enlaces entre notas:** usar wikilinks estilo Obsidian `[[nombre-de-nota]]` cuando tenga sentido; Open WebUI los ignora sin problema y Obsidian los aprovecha.

## Mapeo carpeta → Knowledge Base (sync/config.yaml)

```yaml
knowledge_bases:
  - name: "Prompts"
    paths: ["prompts/"]
  - name: "MCP y Skills"
    paths: ["mcp/", "skills/"]
  - name: "Recursos IA"
    paths: ["recursos/"]
  - name: "Todo"            # KB global con todo el vault, para preguntas amplias
    paths: ["."]
```

El usuario edita este YAML para crear/ajustar el mapeo; el script de sync crea las KBs que no existan.

## Contrato del clasificador (salida JSON)

El LLM clasificador debe devolver **solo** este JSON:

```json
{
  "title": "string",
  "type": "prompt | recurso | nota | snippet | articulo",
  "project": "carpeta-existente-en-vault",
  "tags": ["tag1", "tag2"],
  "summary": "string de 1-2 frases",
  "confidence": 0.0
}
```

- Si `confidence < 0.6`, la app guarda en `inbox/` y lo marca para revisión.
- La lista de carpetas válidas se inyecta dinámicamente en el prompt en cada llamada (leyendo `vault/`).
- Las reglas de criterio (qué cuenta como prompt vs snippet, tags preferidos del usuario, etc.) viven en `capture/classifier_prompt.md` y el usuario las edita en lenguaje natural.
