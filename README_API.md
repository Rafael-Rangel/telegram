# API Telegram Video Downloader

API HTTP para baixar vídeos do Telegram e integrar com n8n.

## 🚀 Instalação e Deploy

### 1. Adicionar ao docker-compose.yml

Adicione o serviço `telegram-video-downloader` ao seu `docker-compose.yml`:

```yaml
  telegram-video-downloader:
    build:
      context: .
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

volumes:
  telegram-session:
```

### 2. Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```bash
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_SUBDOMAIN=telegram-videos  # ou o subdomínio que você quiser
```

### 3. Build e Deploy

```bash
docker-compose build telegram-video-downloader
docker-compose up -d telegram-video-downloader
```

### 4. Primeira Autenticação

Na primeira vez, você precisa autenticar:

```bash
docker exec -it telegram-video-downloader python -c "
from telethon import TelegramClient
import os
client = TelegramClient('telegram_session', os.getenv('TELEGRAM_API_ID'), os.getenv('TELEGRAM_API_HASH'))
import asyncio
asyncio.run(client.start())
"
```

## 📡 Endpoints da API

### GET /health
Verifica status da API

**Resposta:**
```json
{
  "status": "ok",
  "ffmpeg": true,
  "whisper": true
}
```

### POST /download-videos
Baixa vídeos de um grupo do Telegram

**Parâmetros:**
- `grupo_id` (string): ID do grupo (ex: "-1002007723449")
- `limite` (int, opcional): Número máximo de vídeos (padrão: 3)
- `transcrever` (bool, opcional): Se deve transcrever (padrão: true)

**Exemplo de requisição (n8n):**
```
POST http://localhost:8001/download-videos
Content-Type: application/json

{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "3 vídeo(s) baixado(s) com sucesso",
  "videos": [
    {
      "success": true,
      "video_path": "/tmp/telegram-videos/n1002007723449/2025-11-01/video.mp4",
      "transcription_path": "/tmp/telegram-videos/n1002007723449/2025-11-01/video_transcricao.txt",
      "video_id": "-1002007723449_12345_67890",
      "date": "2025-11-01",
      "filename": "video.mp4",
      "size_mb": 23.86,
      "message": "Vídeo baixado com sucesso: video.mp4"
    }
  ],
  "total": 3
}
```

### GET /list-groups
Lista todos os grupos do Telegram

**Resposta:**
```json
{
  "success": true,
  "groups": [
    {
      "id": -1002007723449,
      "title": "🎬 Cortes Prontos - Cortes 10K 🎬",
      "is_group": true,
      "is_channel": false
    }
  ],
  "total": 1
}
```

## 🔗 Integração com n8n

1. Use o nó **HTTP Request** no n8n
2. Configure:
   - Method: POST
   - URL: `http://telegram-video-downloader:8000/download-videos`
   - Body (JSON):
     ```json
     {
       "grupo_id": "-1002007723449",
       "limite": 3,
       "transcrever": true
     }
     ```

3. Os vídeos serão salvos em `/tmp/telegram-videos/` no container
4. Acesse os vídeos via volume montado: `/tmp/telegram-videos` no host

## 📁 Estrutura de Pastas

```
/tmp/telegram-videos/
  └── n1002007723449/  (ID do grupo)
      └── 2025-11-01/
          ├── video1.mp4
          ├── video1_transcricao.txt
          ├── video2.mp4
          └── video2_transcricao.txt
```

## 🔑 Autenticação Telegram

Na primeira execução, você precisa autenticar manualmente. O arquivo de sessão será salvo no volume `telegram-session` e não precisará autenticar novamente.

## ⚠️ Notas Importantes

- **FFmpeg**: Já está incluído no container (não precisa do n8n)
- **Whisper**: Será baixado automaticamente na primeira transcrição
- **Limite**: Máximo de 3 vídeos por requisição (configurável)
- **Controle de duplicatas**: IDs são salvos em `/tmp/telegram-videos/videos_baixados.json`
- **Volumes**: Vídeos são salvos em `/tmp/telegram-videos` (montado do host)

