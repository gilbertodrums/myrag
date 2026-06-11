# Fase 4 — (Futuro/Opcional) Dashboard visual propio

> **No implementar hasta que el usuario lo pida explícitamente y las fases 1-3 lleven semanas en uso.**
> Esta fase existe para que las decisiones de las fases anteriores no la bloqueen.

**Objetivo eventual:** una vista web propia, interactiva y clara, sobre el vault: explorar por proyecto/tipo/tag, buscar, ver estadísticas de capturas, y lanzar un chat con contexto preseleccionado.

## Ideas (a refinar con el usuario en su momento)

- SPA ligera (React + Vite) o app server-rendered con FastAPI + HTMX, servida desde el mismo VPS.
- Lee el vault directamente (los frontmatter son la "base de datos"): índice generado por un script a `index.json`.
- Vistas: tarjetas por proyecto, filtro por tags/tipo, búsqueda full-text, timeline de capturas.
- Botón "Abrir chat con este contexto": deep-link a Open WebUI con la KB correspondiente, o integración con su API de chat.
- Posible vista de grafo (estilo Obsidian) usando los wikilinks.

## Por qué se pospone

- Open WebUI + Obsidian ya cubren el 90% de la necesidad visual al inicio.
- El valor real del dashboard depende de patrones de uso que solo aparecerán tras usar el sistema de verdad.

## Criterio para activar esta fase

El usuario nota fricción concreta que Open WebUI/Obsidian no resuelven (anotarlas en `docs/notas-de-uso.md` cuando ocurran). Esas fricciones definirán los requisitos reales del dashboard.
