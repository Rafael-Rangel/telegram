#!/bin/bash
# Script de instalação rápida do Telegram Video Downloader na VPS

echo "🚀 Instalando Telegram Video Downloader..."

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar se está como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Por favor, execute como root (sudo)${NC}"
    exit 1
fi

# Verificar se docker-compose existe
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}docker-compose não encontrado!${NC}"
    exit 1
fi

# Verificar se os arquivos necessários existem
if [ ! -f "api.py" ] || [ ! -f "Dockerfile.telegram" ]; then
    echo -e "${RED}Arquivos necessários não encontrados!${NC}"
    echo "Certifique-se de estar no diretório com os arquivos do projeto."
    exit 1
fi

echo -e "${GREEN}✓ Arquivos encontrados${NC}"

# Perguntar variáveis de ambiente
read -p "TELEGRAM_API_ID [29090427]: " API_ID
API_ID=${API_ID:-29090427}

read -p "TELEGRAM_API_HASH [88bf96af8dc0652c6f5026417b7d8f25]: " API_HASH
API_HASH=${API_HASH:-88bf96af8dc0652c6f5026417b7d8f25}

read -p "TELEGRAM_SUBDOMAIN [telegram-videos]: " SUBDOMAIN
SUBDOMAIN=${SUBDOMAIN:-telegram-videos}

# Criar diretório para o projeto
PROJECT_DIR="$HOME/telegram-downloader"
mkdir -p $PROJECT_DIR
cp api.py telegram_client.py config.py requirements.txt Dockerfile.telegram $PROJECT_DIR/

echo -e "${GREEN}✓ Arquivos copiados para $PROJECT_DIR${NC}"

# Criar arquivo .env se não existir
ENV_FILE="$HOME/.env"
if [ ! -f "$ENV_FILE" ]; then
    touch $ENV_FILE
fi

# Adicionar variáveis ao .env
grep -q "TELEGRAM_API_ID" $ENV_FILE || echo "TELEGRAM_API_ID=$API_ID" >> $ENV_FILE
grep -q "TELEGRAM_API_HASH" $ENV_FILE || echo "TELEGRAM_API_HASH=$API_HASH" >> $ENV_FILE
grep -q "TELEGRAM_SUBDOMAIN" $ENV_FILE || echo "TELEGRAM_SUBDOMAIN=$SUBDOMAIN" >> $ENV_FILE

echo -e "${GREEN}✓ Variáveis de ambiente configuradas${NC}"

# Mostrar o que adicionar ao docker-compose.yml
echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Adicione este serviço ao seu docker-compose.yml:${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cat << 'EOF'

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

# E adicione 'telegram-session:' na seção volumes:
volumes:
  ...
  telegram-session:

EOF

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${GREEN}Próximos passos:${NC}"
echo "1. Edite seu docker-compose.yml e adicione o serviço acima"
echo "2. Execute: docker-compose build telegram-video-downloader"
echo "3. Execute: docker-compose up -d telegram-video-downloader"
echo "4. Autentique no Telegram (veja GUIA_INSTALACAO_VPS.md)"
echo -e "\n${GREEN}✓ Instalação preparada!${NC}"

