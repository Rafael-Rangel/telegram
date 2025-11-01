#!/bin/bash
# Script para limpar arquivos desnecessários na VPS

cd ~/telegram-downloader

echo "🧹 Limpando arquivos desnecessários..."

# Remover arquivos de outros serviços/deploy
rm -f app_gui.py
rm -f app_web.py
rm -f Procfile
rm -f pyproject.toml
rm -f railway.json
rm -f runtime.txt
rm -f uv.lock
rm -f vercel.json
rm -rf templates/

# Remover documentação redundante (manter apenas os principais)
rm -f ADICIONAR_AO_DOCKER_COMPOSE.yml
rm -f ARQUIVOS_PARA_GITHUB.md
rm -f COMANDOS_VPS.txt
rm -f COMANDOS_VPS_EXATOS.txt
rm -f COMO_ENVIAR_GITHUB.md
rm -f RESUMO_UPLOAD.md
rm -f GUIA_INSTALACAO_VPS.md
rm -f INSTALL.sh
rm -f docker-compose-final.yml

# Manter apenas:
# - api.py
# - telegram_client.py
# - config.example.py
# - requirements.txt
# - Dockerfile.telegram
# - README.md
# - README_API.md
# - INSTRUCOES_VPS.md ou PROXIMO_PASSO_VPS.md (escolher um)
# - docker-compose.addition.yml (referência)

echo "✅ Limpeza concluída!"
echo ""
echo "Arquivos restantes:"
ls -la

