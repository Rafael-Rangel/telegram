# 🚀 Próximo Passo: Instalar na VPS

## ✅ Você já fez:
- [x] Código funcionando localmente
- [x] Upload para GitHub

## 📋 Agora: Instalar na VPS

### Passo 1: Conectar na VPS e Clonar

```bash
# Na sua VPS (SSH)
cd ~
git clone https://github.com/Rafael-Rangel/telegram.git telegram-downloader
cd telegram-downloader
ls -la  # Verificar arquivos
```

### Passo 2: Editar docker-compose.yml

```bash
cd ~
nano docker-compose.yml
```

**Adicione ANTES da linha `volumes:`** (depois do serviço `postiz-legal`):

```yaml
  telegram-video-downloader:
    build:
      context: ./telegram-downloader
      dockerfile: Dockerfile.telegram
    container_name: telegram-video-downloader
    restart: always
    ports:
      - "127.0.0.1:8001:8000"
    environment:
      - TELEGRAM_API_ID=${TELEGRAM_API_ID}
      - TELEGRAM_API_HASH=${TELEGRAM_API_HASH}
      - TELEGRAM_SESSION_NAME=telegram_session
    volumes:
      - /tmp/telegram-videos:/tmp/telegram-videos
      - telegram-session:/app/.telegram_session
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.telegram-downloader.rule=Host(`${TELEGRAM_SUBDOMAIN}.${DOMAIN_NAME}`)"
      - "traefik.http.routers.telegram-downloader.tls=true"
      - "traefik.http.routers.telegram-downloader.entrypoints=web,websecure"
      - "traefik.http.routers.telegram-downloader.tls.certresolver=mytlschallenge"
      - "traefik.http.services.telegram-downloader.loadbalancer.server.port=8000"
```

**E na seção `volumes:`, adicione:**

```yaml
volumes:
  traefik_data:
    external: true
  n8n_data:
    external: true
  postgres-volume:
  postiz-config:
  postiz-uploads:
  postiz-redis-data:
  telegram-session:  # ← ADICIONE ESTA LINHA
```

### Passo 3: Configurar .env

```bash
nano .env
```

Adicione estas linhas (se não existirem):

```bash
TELEGRAM_API_ID=29090427
TELEGRAM_API_HASH=88bf96af8dc0652c6f5026417b7d8f25
TELEGRAM_SUBDOMAIN=telegram-videos
```

### Passo 4: Build e Iniciar

```bash
docker-compose build telegram-video-downloader
docker-compose up -d telegram-video-downloader
```

### Passo 5: Verificar

```bash
# Ver se está rodando
docker ps | grep telegram

# Ver logs
docker logs telegram-video-downloader
```

### Passo 6: Autenticar no Telegram (PRIMEIRA VEZ)

```bash
docker exec -it telegram-video-downloader python3 -c "
import asyncio
from telethon import TelegramClient
async def auth():
    client = TelegramClient('telegram_session', 29090427, '88bf96af8dc0652c6f5026417b7d8f25')
    await client.start()
    print('✅ Autenticado!')
    await client.disconnect()
asyncio.run(auth())
"
```

**Você precisará:**
1. Digitar número: `+5521991305454`
2. Código do Telegram
3. Senha 2FA (se tiver)

### Passo 7: Testar API

```bash
# Health check
curl http://localhost:8001/health

# Listar grupos
curl http://localhost:8001/list-groups
```

### Passo 8: Usar no n8n

No n8n, crie um workflow com nó **HTTP Request**:

- **URL:** `http://telegram-video-downloader:8000/download-videos`
- **Method:** POST
- **Body (JSON):**
```json
{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true
}
```

## ✅ Pronto!

Seu serviço estará rodando e integrado com n8n!

## 🔍 Comandos Úteis

```bash
# Ver logs em tempo real
docker logs -f telegram-video-downloader

# Reiniciar
docker-compose restart telegram-video-downloader

# Ver vídeos baixados
ls -lh /tmp/telegram-videos/
```

## ⚠️ Se der erro

```bash
# Ver logs detalhados
docker logs telegram-video-downloader

# Rebuild se necessário
docker-compose build --no-cache telegram-video-downloader
docker-compose up -d telegram-video-downloader
```

