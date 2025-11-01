"""
Configurações do Telegram - EXEMPLO
Copie este arquivo para config.py e preencha com suas credenciais
"""
import os

# Credenciais do Telegram
# Obtenha em: https://my.telegram.org/apps
API_ID = int(os.getenv("TELEGRAM_API_ID", "SEU_API_ID_AQUI"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "SEU_API_HASH_AQUI")

# Nome da sessão (arquivo de sessão será criado automaticamente)
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_session")

