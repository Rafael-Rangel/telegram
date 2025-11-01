# 📥 Telegram Video Downloader API

API para baixar vídeos do Telegram automaticamente, transcrever com Whisper e integrar com n8n.

## 🚀 Funcionalidades

- ✅ Download automático de vídeos de grupos do Telegram
- ✅ Transcrição automática usando Whisper (OpenAI) - **100% GRATUITO**
- ✅ API HTTP para integração com n8n
- ✅ Controle de duplicatas (não baixa vídeos repetidos)
- ✅ Limite configurável de vídeos por requisição (padrão: 3)
- ✅ Organização automática por grupo e data
- ✅ Retorna: vídeo, transcrição, ID, data, tamanho

## 📋 Requisitos

- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local)
- FFmpeg (incluído no Dockerfile)
- Conta no Telegram com API_ID e API_HASH

## 🔧 Instalação

### Para VPS com Docker

Veja o guia completo em: [GUIA_INSTALACAO_VPS.md](GUIA_INSTALACAO_VPS.md)

**Resumo rápido:**
1. Clone este repositório na sua VPS
2. Adicione o serviço ao seu `docker-compose.yml`
3. Execute `docker-compose build && docker-compose up -d`
4. Autentique no Telegram (primeira vez)

### Para desenvolvimento local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar API
uvicorn api:app --host 0.0.0.0 --port 8000

# Ou executar script local
python telegram_client.py
```

## 📡 API Endpoints

### GET /health
Verifica status da API

### POST /download-videos
Baixa vídeos de um grupo

**Parâmetros:**
- `grupo_id` (string): ID do grupo Telegram
- `limite` (int, opcional): Máximo de vídeos (padrão: 3)
- `transcrever` (bool, opcional): Transcrever vídeos (padrão: true)

**Exemplo:**
```json
{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true
}
```

### GET /list-groups
Lista todos os grupos do Telegram

## 🔗 Integração com n8n

Use o nó **HTTP Request**:

```
URL: http://telegram-video-downloader:8000/download-videos
Method: POST
Body: JSON
{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true
}
```

## 📁 Estrutura de Arquivos

```
.
├── api.py                    # API FastAPI principal
├── telegram_client.py        # Funções do cliente Telegram
├── config.py                 # Configurações
├── requirements.txt          # Dependências Python
├── Dockerfile.telegram       # Dockerfile para container
├── docker-compose.addition.yml  # Serviço para adicionar ao compose
├── GUIA_INSTALACAO_VPS.md    # Guia completo de instalação
├── README_API.md             # Documentação da API
└── README.md                 # Este arquivo
```

## 🎤 Transcrição com Whisper

- **100% Gratuito**: Whisper roda localmente, sem custos
- **Offline**: Não envia dados para servidores
- **Suporta Português**: Configurado para PT-BR
- **Modelo**: "base" (equilíbrio entre velocidade e qualidade)

## ⚙️ Configuração

Crie um arquivo `.env` (ou use variáveis de ambiente):

```bash
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_SESSION_NAME=telegram_session
```

**Como obter API_ID e API_HASH:**
1. Acesse https://my.telegram.org/apps
2. Faça login
3. Crie uma nova aplicação
4. Copie o API_ID e API_HASH

## 📝 Licença

Este projeto é de uso pessoal/educacional.

## 🤝 Contribuições

Este é um projeto pessoal, mas sugestões são bem-vindas!

## 📚 Documentação Adicional

- [Guia de Instalação na VPS](GUIA_INSTALACAO_VPS.md)
- [Documentação da API](README_API.md)
- [Comandos para VPS](COMANDOS_VPS.txt)
