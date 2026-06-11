# Fase 1 — Infraestructura: VPS + Open WebUI + OpenRouter

**Objetivo:** al terminar esta fase, el usuario puede entrar a `https://chat.<dominio>` desde cualquier dispositivo, chatear con varios modelos vía OpenRouter, y adjuntar archivos a un chat.

**Prerrequisitos (los provee el usuario, pídelos si faltan):**
- Acceso SSH a un VPS con Ubuntu 22.04+ y 2 GB RAM.
- Un dominio o subdominio apuntando a la IP del VPS.
- API key de OpenRouter.

## Pasos

1. **Preparar el VPS**
   - Crear usuario no-root con sudo, configurar SSH por llave, deshabilitar login root por password.
   - Firewall (ufw): permitir solo 22, 80, 443.
   - Instalar Docker y el plugin de Docker Compose.

2. **Escribir `infra/docker-compose.yml`** con dos servicios:
   - `open-webui`: imagen oficial, volumen persistente para datos, variables de entorno desde `.env` (`OPENAI_API_BASE_URL` apuntando a OpenRouter, `OPENAI_API_KEY`).
   - `caddy`: reverse proxy con HTTPS automático hacia open-webui. Incluir `infra/Caddyfile`.
   - Ninguna imagen expone puertos directamente salvo Caddy (80/443).

3. **Levantar y configurar Open WebUI**
   - `docker compose up -d`, verificar logs sin errores.
   - Guiar al usuario: crear la cuenta admin en el primer acceso.
   - Tras crear la cuenta: poner `ENABLE_SIGNUP=false` y reiniciar.
   - Verificar que aparecen los modelos de OpenRouter en el selector. Recomendar al usuario fijar 4-6 modelos favoritos como visibles.

4. **Generar la API key de Open WebUI** (Settings → Account) y guardarla en el `.env` del VPS — se usará en la Fase 2.

5. **Documentar** en `infra/README.md`: cómo levantar, actualizar (`docker compose pull && up -d`), ver logs, y hacer backup del volumen.

## Criterios de aceptación

- [ ] `https://chat.<dominio>` carga con certificado válido desde PC y móvil.
- [ ] El registro de nuevas cuentas está deshabilitado.
- [ ] Un chat con al menos 2 modelos distintos de OpenRouter responde correctamente.
- [ ] Se puede adjuntar un `.md` a un chat y el modelo responde sobre su contenido.
- [ ] `docker compose config` valida sin errores; los servicios sobreviven a un reinicio del VPS (`restart: unless-stopped`).
- [ ] No hay ningún secreto commiteado en el repo (`git log -p | grep -i key` limpio; existe `.env.example`).

## Verificación

```bash
docker compose -f infra/docker-compose.yml config
docker compose -f infra/docker-compose.yml ps   # todos "running/healthy"
curl -I https://chat.<dominio>                  # 200/302 con HTTPS
```
