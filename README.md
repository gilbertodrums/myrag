# Knowledge Hub — Diseño del proyecto

Sistema personal de gestión de conocimiento con chat de IA: notas en Markdown (Git) + Open WebUI (RAG multi-modelo vía OpenRouter) + captura rápida con clasificación automática por LLM.

## Cómo usar este paquete con tu agente de IA

1. Crea un repo nuevo (privado) en GitHub, p. ej. `knowledge-hub`.
2. Copia todos estos archivos a la raíz del repo y haz el primer commit.
3. Abre tu agente (Claude Code, etc.) en el repo y dile:

   > Lee AGENTS.md y los docs. Empieza por tasks/fase-1-infraestructura.md.
   > No avances de fase sin cumplir y verificar los criterios de aceptación.

4. El agente te irá pidiendo lo que necesita (acceso al VPS, dominio, API key de OpenRouter).

## Mapa de archivos

| Archivo | Qué contiene |
|---|---|
| `AGENTS.md` | Arnés del agente: reglas, stack, convenciones, orden de trabajo |
| `docs/00-vision.md` | El problema, objetivos y prioridades |
| `docs/01-arquitectura.md` | Diagrama, componentes, flujos y decisiones |
| `docs/02-stack.md` | Tecnologías, variables de entorno |
| `docs/03-estructura-datos.md` | Estructura del vault, frontmatter, contrato del clasificador |
| `tasks/fase-1-infraestructura.md` | VPS + Open WebUI + OpenRouter |
| `tasks/fase-2-sync.md` | Vault + sincronización a Knowledge Bases |
| `tasks/fase-3-captura.md` | App de captura + clasificador LLM |
| `tasks/fase-4-dashboard.md` | Dashboard futuro (pospuesto a propósito) |

## Qué necesitas tener antes de empezar

- [ ] VPS con Ubuntu 22.04+ y 2 GB RAM (~$5/mes: Hetzner, DigitalOcean, etc.)
- [ ] Un dominio o subdominio apuntando al VPS
- [ ] API key de OpenRouter con algo de crédito
- [ ] Repo privado en GitHub para este proyecto
