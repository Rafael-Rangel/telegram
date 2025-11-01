# 🚀 Guia de Instalação na VPS

## Passo 1: Preparar os arquivos na VPS

### Opção A: Usando Git (Recomendado)

```bash
# Na sua VPS
cd ~
git clone [seu-repositorio] telegram-downloader
cd telegram-downloader
```

### Opção B: Transferir arquivos manualmente

1. **No seu computador local**, compacte os arquivos:
   ```bash
   # No Windows (PowerShell)
   Compress-Archive -Path api.py,telegram_client.py,config.py,requirements.txt,Dockerfile.telegram -DestinationPath telegram-downloader.zip
   ```

2. **Transfira para a VPS** (use SCP, SFTP ou WinSCP):
   ```bash
   # Exemplo com SCP (do seu PC)
   scp telegram-downloader.zip root@93.127.211.69:~/
   ```

3. **Na VPS**, descompacte:
   ```bash
   cd ~
   unzip telegram-downloader.zip -d telegram-downloader
   cd telegram-downloader
   ```

## Passo 2: Editar o docker-compose.yml

```bash
# Na sua VPS
cd ~
nano docker-compose.yml
# ou
vi docker-compose.yml
```

**Adicione o serviço `telegram-video-downloader` ANTES da seção `volumes:`:**

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

volumes:
  traefik_data:
    external: true
  n8n_data:
    external: true
  postgres-volume:
  postiz-config:
  postiz-uploads:
  postiz-redis-data:
  telegram-session:  # ADICIONE ESTA LINHA
```

## Passo 3: Adicionar variáveis de ambiente

```bash
# Verifique se você tem um arquivo .env
ls -la .env

# Se não existir, crie um baseado no que você tem
# Adicione estas linhas ao seu .env (ou crie se não existir):
```

Crie ou edite o arquivo `.env`:

```bash
nano .env
```

**Adicione estas variáveis:**

```bash
# Telegram Video Downloader
TELEGRAM_API_ID=29090427
TELEGRAM_API_HASH=88bf96af8dc0652c6f5026417b7d8f25
TELEGRAM_SUBDOMAIN=telegram-videos  # ou o subdomínio que você quiser usar
```

## Passo 4: Build e Deploy

```bash
# Build do novo serviço
docker-compose build telegram-video-downloader

# Iniciar o serviço
docker-compose up -d telegram-video-downloader

# Verificar se está rodando
docker ps | grep telegram-video-downloader

# Ver logs
docker logs telegram-video-downloader
```

## Passo 5: Autenticação no Telegram (PRIMEIRA VEZ)

**IMPORTANTE:** Na primeira vez, você precisa autenticar manualmente:

```bash
# Entrar no container
docker exec -it telegram-video-downloader bash

# Dentro do container, execute:
python3 -c "
import asyncio
from telethon import TelegramClient
import os

async def auth():
    client = TelegramClient(
        os.getenv('TELEGRAM_SESSION_NAME', 'telegram_session'),
        int(os.getenv('TELEGRAM_API_ID')),
        os.getenv('TELEGRAM_API_HASH')
    )
    await client.start()
    print('✅ Autenticado com sucesso!')
    await client.disconnect()

asyncio.run(auth())
"
```

Você será solicitado a:
1. Digitar seu número de telefone (com código do país, ex: +5521991305454)
2. Digitar o código de verificação do Telegram
3. Se tiver 2FA, digitar a senha

Após autenticar, a sessão será salva e não precisará autenticar novamente.

## Passo 6: Testar a API

```bash
# Verificar saúde da API
curl http://localhost:8001/health

# Listar grupos
curl http://localhost:8001/list-groups

# Baixar vídeos (exemplo)
curl -X POST http://localhost:8001/download-videos \
  -H "Content-Type: application/json" \
  -d '{
    "grupo_id": "-1002007723449",
    "limite": 3,
    "transcrever": true
  }'
```

## Passo 7: Integrar com n8n

No n8n, use o nó **HTTP Request**:

1. **Method:** POST
2. **URL:** `http://telegram-video-downloader:8000/download-videos`
3. **Body Type:** JSON
4. **Body:**
   ```json
   {
     "grupo_id": "-1002007723449",
     "limite": 3,
     "transcrever": true
   }
   ```

## Passo 8: Verificar os vídeos baixados

```bash
# Verificar vídeos no host
ls -lh /tmp/telegram-videos/

# Ver estrutura
tree /tmp/telegram-videos/  # se tiver tree instalado
# ou
find /tmp/telegram-videos/ -type f
```

## ⚠️ Troubleshooting

### Container não inicia
```bash
docker logs telegram-video-downloader
```

### Erro de autenticação
```bash
# Remover sessão antiga e tentar novamente
docker exec telegram-video-downloader rm -f /app/.telegram_session/*.session
# Depois refazer autenticação (Passo 5)
```

### FFmpeg não encontrado
```bash
# Verificar dentro do container
docker exec telegram-video-downloader ffmpeg -version
```

### Porta já em uso
```bash
# Verificar se a porta 8001 está livre
netstat -tulpn | grep 8001
# Ou mude a porta no docker-compose.yml
```

## 📋 Comandos Úteis

```bash
# Parar o serviço
docker-compose stop telegram-video-downloader

# Reiniciar
docker-compose restart telegram-video-downloader

# Ver logs em tempo real
docker logs -f telegram-video-downloader

# Rebuild após mudanças
docker-compose build telegram-video-downloader
docker-compose up -d telegram-video-downloader

# Limpar vídeos antigos (cuidado!)
rm -rf /tmp/telegram-videos/*
```

## ✅ Checklist Final

- [ ] Arquivos transferidos para VPS
- [ ] Serviço adicionado ao docker-compose.yml
- [ ] Variáveis de ambiente configuradas
- [ ] Container buildado e rodando
- [ ] Autenticação Telegram realizada
- [ ] API testada e funcionando
- [ ] Integração n8n configurada
- [ ] Vídeos salvando em /tmp/telegram-videos

