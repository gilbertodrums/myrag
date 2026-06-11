# Fase 3 — Captura rápida + clasificador LLM

**Objetivo:** el usuario pega un texto desde cualquier dispositivo, la IA lo clasifica (título, tipo, proyecto, tags, resumen), y la nota termina en el vault y en Open WebUI sin pasos manuales.

**Depende de:** Fase 2 completa.

## Pasos

1. **App FastAPI en `capture/`:**
   - `GET /` → página HTML mínima y agradable en móvil: textarea grande, campo opcional de URL de origen, botón "Capturar". Protegida por token (`?t=<CAPTURE_TOKEN>` o header).
   - `POST /capture` → recibe el texto, llama al clasificador, devuelve la propuesta.
   - La página muestra la clasificación propuesta (editable: título, proyecto, tags) con botones **Guardar** y **Guardar en inbox**.
   - `POST /save` → genera el `.md` con frontmatter (esquema de `docs/03-estructura-datos.md`), lo escribe en la carpeta correcta del clon local del vault, y hace `git add/commit/push`.

2. **Clasificador (`capture/classifier.py`):**
   - Llama a OpenRouter con el modelo de `CLASSIFIER_MODEL`.
   - El system prompt se construye desde `capture/classifier_prompt.md` (editable por el usuario) + la lista de carpetas válidas leída dinámicamente del vault.
   - Exige salida JSON estricta según el contrato de `docs/03-estructura-datos.md`; validar con Pydantic. Si el JSON es inválido, reintentar 1 vez; si falla, guardar en `inbox/` con metadatos mínimos.
   - Si `confidence < 0.6` → destino `inbox/`.

3. **Escribir `capture/classifier_prompt.md` inicial** con reglas sensatas (qué es un prompt vs snippet vs recurso, estilo de tags, idioma de títulos) y comentarios explicando al usuario cómo personalizarlo.

4. **Dockerizar:** añadir el servicio `capture` al `docker-compose.yml` y exponerlo vía Caddy en `https://capt.<dominio>` (o ruta `/capture`). El contenedor necesita el clon del vault y llave SSH de deploy para push (documentar setup de deploy key con permisos de escritura solo a ese repo).

5. **(Opcional, si el usuario lo pide) Bot de Telegram:** mismo backend, cada mensaje al bot = una captura; el bot responde con la clasificación y botones de confirmar/inbox.

6. **Probar el flujo de punta a punta:** pegar un prompt real → clasificado → guardado → push → sync → preguntarle a Open WebUI por él.

## Criterios de aceptación

- [ ] Desde el móvil: pegar texto → ver clasificación propuesta → guardar, en menos de 30 segundos.
- [ ] La nota generada cumple el esquema de frontmatter y queda en la carpeta correcta.
- [ ] Texto ambiguo (p. ej. "hola probando") termina en `inbox/`, no inventa proyecto.
- [ ] El commit aparece en GitHub con mensaje claro (`feat(vault): captura "..."`).
- [ ] Editar `classifier_prompt.md` cambia el comportamiento sin tocar código (probar con una regla nueva, p. ej. "todo lo que mencione MCP va a la carpeta mcp").
- [ ] Sin token válido, la app rechaza las peticiones (401).
- [ ] Tests del clasificador con respuestas LLM mockeadas: JSON válido, JSON inválido, baja confianza. `ruff` y `pytest` pasan.
- [ ] Ningún secreto en el repo; el contenedor recibe todo por `.env`.

## Verificación

```bash
uv run ruff check capture/
uv run pytest capture/
docker compose -f infra/docker-compose.yml up -d capture
curl -X POST https://capt.<dominio>/capture -H "X-Token: $CAPTURE_TOKEN" -d '{"text":"..."}'
```
