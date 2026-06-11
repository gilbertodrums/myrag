---
title: "Introducción al Model Context Protocol (MCP)"
type: recurso
project: mcp
tags: [mcp, arquitectura, agentes]
source: "manual"
created: 2026-06-11
summary: "Conceptos básicos sobre cómo MCP permite a los LLMs conectarse a fuentes de datos y herramientas locales de forma estándar."
---

El **Model Context Protocol (MCP)** es una arquitectura estándar que permite a los Modelos de Lenguaje Grandes (LLMs) interactuar con herramientas, bases de datos y sistemas locales de manera segura.

## Componentes principales

1. **MCP Client:** Es la aplicación que interactúa con el usuario (ej. Claude Desktop, Open WebUI).
2. **MCP Server:** Un servidor ligero (que puede correr localmente) que expone recursos, prompts y herramientas.
3. **Transport Layer:** Típicamente STDIO o SSE, permite la comunicación bidireccional entre cliente y servidor.

Lo más importante del MCP es que elimina la necesidad de escribir integraciones "ad-hoc" para cada modelo o plataforma. Una vez escribes un MCP Server, cualquier cliente compatible puede consumirlo.
