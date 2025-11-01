# 📋 Instruções para Adicionar na Sua VPS

## Passo 1: Clonar o Repositório

```bash
cd ~
git clone https://github.com/Rafael-Rangel/telegram.git telegram-downloader
cd telegram-downloader
ls -la  # Verificar arquivos
```

## Passo 2: Adicionar ao docker-compose.yml

Edite seu `docker-compose.yml` que está em `~/docker-compose.yml`:

```bash
cd ~
nano docker-compose.yml
```

### Adicione este serviço ANTES da linha `volumes:`:

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

### E na seção `volumes:`, adicione:

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

## Passo 3: Configurar Variáveis de Ambiente

Adicione ao seu arquivo `.env` (ou crie se não existir):

```bash
nano .env
```

Adicione estas linhas:

```bash
TELEGRAM_API_ID=29090427
TELEGRAM_API_HASH=88bf96af8dc0652c6f5026417b7d8f25
TELEGRAM_SUBDOMAIN=telegram-videos
```

## Passo 4: Build e Iniciar

```bash
# Build do serviço
docker-compose build telegram-video-downloader

# Iniciar
docker-compose up -d telegram-video-downloader

# Verificar se está rodando
docker ps | grep telegram
```

## Passo 5: Autenticação Telegram (PRIMEIRA VEZ)

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

Você será pedido para:
1. Número de telefone: `+5521991305454`
2. Código de verificação do Telegram
3. Senha 2FA (se tiver)

## Passo 6: Testar

```bash
# Health check
curl http://localhost:8001/health

# Listar grupos
curl http://localhost:8001/list-groups
```

## Passo 7: Usar no n8n

No n8n, configure um nó **HTTP Request**:

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

## 📁 Estrutura Final

```
~
├── docker-compose.yml         (editado - adicione o serviço)
├── .env                       (editado - adicione variáveis)
├── Dockerfile                 (seu Dockerfile do n8n - não mexer)
└── telegram-downloader/       (novo - clonado do GitHub)
    ├── api.py
    ├── telegram_client.py
    ├── Dockerfile.telegram
    └── ...
```

## ⚠️ Observações Importantes

1. **Context do build:** `./telegram-downloader` - precisa estar na mesma pasta que o docker-compose.yml
2. **Porta:** `127.0.0.1:8001:8000` - acessível apenas localmente na VPS
3. **Vídeos:** Salvos em `/tmp/telegram-videos/` no host
4. **Sessão:** Persiste no volume `telegram-session`

## 🔍 Verificar Logs

```bash
docker logs telegram-video-downloader
docker logs -f telegram-video-downloader  # tempo real
```

## 🔄 Comandos Úteis

```bash
# Reiniciar
docker-compose restart telegram-video-downloader

# Parar
docker-compose stop telegram-video-downloader

# Rebuild após mudanças
docker-compose build telegram-video-downloader
docker-compose up -d telegram-video-downloader
```

