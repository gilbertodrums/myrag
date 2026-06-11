# 00 — Visión y objetivos

## El problema

El usuario sigue de cerca los avances en IA: lanzamientos, proyectos, prompts, MCPs, skills, artículos. Encuentra constantemente información valiosa (casi siempre texto) pero no tiene un lugar único donde guardarla organizada y, sobre todo, **consultarla conversando con una IA**. El código ya vive en GitHub; falta el equivalente para el conocimiento.

## El objetivo

Un sistema personal donde el usuario pueda:

1. **Capturar rápido:** copiar un texto (un prompt, un artículo, un recurso de MCP), pegarlo, y asignarlo a un proyecto en segundos — o dejar que la IA lo clasifique sola.
2. **Preguntar a su conocimiento:** abrir un chat y decir *"¿tengo un prompt que me ayude a diseñar un MCP?"* y que el agente busque por contexto (semánticamente, no solo por palabra exacta) en su base personal.
3. **Elegir el modelo:** usar OpenRouter o sus propias API keys para cambiar de modelo según la tarea.
4. **Adjuntar contexto extra:** en cualquier chat, poder añadir archivos puntuales además de la base de conocimiento.
5. **Crecer poco a poco:** empezar simple y que el sistema escale sin migraciones dolorosas.

## Prioridades del usuario (en orden)

1. Que el chat responda sobre sus notas (RAG).
2. Que la IA organice/etiquete lo que guarda.
3. Captura rápida (pegar y asignar a proyecto).
4. Vista visual e interactiva de todo.

## Principios de diseño

- **Los datos son del usuario:** Markdown plano en un repo Git. Cualquier herramienta (Obsidian, Open WebUI, un dashboard futuro) es una "vista" reemplazable sobre esos archivos.
- **Adaptar antes que construir:** Open WebUI resuelve el chat + RAG + multi-modelo de forma madura. El esfuerzo de desarrollo propio se concentra donde no hay solución existente: la captura inteligente y las reglas de organización personalizadas.
- **Acceso desde cualquier lado:** todo lo interactivo es web, hosteado en un VPS del usuario (~$5/mes).
- **Cada fase entrega valor por sí sola:** la Fase 1 ya es usable sin las demás.

## Qué NO es este proyecto

- No es una app multiusuario ni un producto comercial.
- No es un reemplazo de GitHub para código.
- No requiere entrenar ni fine-tunear modelos: todo es RAG + prompting.
