# Fase 2 — Vault + Sync (repo → Open WebUI)

**Objetivo:** las notas markdown del repo aparecen automáticamente en las Knowledge Bases de Open WebUI, y el usuario puede preguntar a un chat sobre ellas.

**Depende de:** Fase 1 completa (Open WebUI corriendo + API key generada).

## Pasos

1. **Crear la estructura del vault** según `docs/03-estructura-datos.md`, con 3-5 notas de ejemplo reales que cumplan el esquema de frontmatter (pedir al usuario contenido real: un par de prompts suyos, un recurso de MCP).

2. **Investigar la API actual de Open WebUI** para Knowledge Bases (crear KB, subir archivo, actualizar, eliminar). Consultar https://docs.openwebui.com — no asumir endpoints de memoria.

3. **Escribir `sync/sync.py`:**
   - Lee `sync/config.yaml` (mapeo carpetas → KBs).
   - Crea las KBs que no existan.
   - Calcula hash de cada `.md` del vault; mantiene un estado local (`sync/.state.json`) para detectar nuevos/modificados/borrados.
   - Sube, actualiza o elimina archivos en la KB correspondiente vía API.
   - Idempotente: correrlo dos veces seguidas no hace nada la segunda vez.
   - Logging claro en español de qué hizo.

4. **Automatizar:** cron en el VPS cada 15 minutos que hace `git pull` del vault y corre el sync. (Alternativa si el usuario prefiere: GitHub Action en cada push que llama al sync remotamente.)

5. **Probar el flujo completo:** editar una nota → push → esperar sync → preguntar en un chat de Open WebUI con la KB asociada y verificar que la respuesta usa la nota.

## Criterios de aceptación

- [ ] `vault/` existe con la estructura definida y notas de ejemplo válidas.
- [ ] `uv run python sync/sync.py` crea las KBs y sube las notas; la segunda ejecución reporta "0 cambios".
- [ ] Modificar una nota y re-ejecutar actualiza solo esa nota; borrarla la elimina de la KB.
- [ ] En Open WebUI, un chat asociado a la KB "Prompts" responde correctamente a una pregunta cuyo dato está solo en una nota (p. ej. "¿tengo un prompt para diseñar un MCP?").
- [ ] El cron está activo y registra sus ejecuciones en un log.
- [ ] `ruff check sync/` pasa sin errores; hay al menos un test del cálculo de difs (`uv run pytest`).

## Verificación

```bash
uv run ruff check sync/
uv run pytest sync/
uv run python sync/sync.py          # primera vez: sube todo
uv run python sync/sync.py          # segunda vez: "0 cambios"
crontab -l | grep sync              # cron instalado
```
