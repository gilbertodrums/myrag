# Operaciones de Infraestructura - Knowledge Hub

Este directorio contiene las configuraciones de Docker Compose para levantar Open WebUI localmente y en el VPS (producción).

---

## 💻 Desarrollo Local (Windows / Mac / Linux)

### Requisitos
- **Docker Desktop** instalado y corriendo.
- Clave API de **OpenRouter**.

### 1. Iniciar localmente
En la raíz del proyecto, asegúrate de que el archivo `.env` tenga tu clave de OpenRouter:
```ini
OPENROUTER_API_KEY=tu_api_key_aqui
```

Luego levanta el contenedor local usando la configuración local:
```powershell
docker compose --env-file .env -f infra/docker-compose.local.yml up -d
```

### 2. Acceder al servicio
Abre en tu navegador la dirección:
👉 **[http://localhost:3000](http://localhost:3000)**

*Nota: La primera cuenta registrada será automáticamente la cuenta **Administradora**.*

### 3. Ver logs y detener
- Ver los logs del servicio local:
  ```powershell
  docker compose --env-file .env -f infra/docker-compose.local.yml logs -f open-webui
  ```
- Detener los contenedores locales (conservando datos):
  ```powershell
  docker compose --env-file .env -f infra/docker-compose.local.yml down
  ```
- Detener y borrar datos del volumen (reinicio completo de base de datos):
  ```powershell
  docker compose --env-file .env -f infra/docker-compose.local.yml down -v
  ```

---

## 🌐 Producción (VPS Ubuntu)

Una vez probado en local y cuando tengas un dominio configurado apuntando a la IP pública de tu VPS:

### 1. Preparar el VPS
1. Conéctate a tu VPS e instala Docker y Docker Compose:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-v2
   ```
2. Habilita y configura el firewall UFW:
   ```bash
   sudo ufw allow 22/tcp   # SSH
   sudo ufw allow 80/tcp   # HTTP para Caddy
   sudo ufw allow 443/tcp  # HTTPS para Caddy
   sudo ufw enable
   ```

### 2. Configurar y Desplegar
1. Copia el contenido de la carpeta `infra/` y el archivo `.env` al VPS.
2. Edita `infra/Caddyfile` en el VPS reemplazando `chat.tudominio.com` y `your-email@example.com` con tus datos reales.
3. Levanta la configuración de producción:
   ```bash
   docker compose -f infra/docker-compose.yml up -d
   ```
4. Caddy gestionará e instalará los certificados SSL automáticamente. Podrás acceder en:
   👉 `https://chat.tudominio.com`

### 3. Actualizar la aplicación
Para actualizar Open WebUI a la última versión:
```bash
docker compose -f infra/docker-compose.yml pull
docker compose -f infra/docker-compose.yml up -d --remove-orphans
```

### 4. Backups de base de datos
Los datos de Open WebUI (chats, configuraciones, usuarios) se guardan en el volumen de Docker. Puedes hacer un backup comprimido de ese volumen ejecutando:
```bash
docker run --rm -v open-webui-data:/volume -v $(pwd):/backup alpine tar czf /backup/open-webui-backup.tar.gz -C /volume .
```
