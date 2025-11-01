# 📤 Arquivos para Enviar ao GitHub

## ✅ Arquivos NECESSÁRIOS (enviar)

1. **api.py** - API principal FastAPI
2. **telegram_client.py** - Funções do cliente Telegram
3. **config.py** - Configurações (será criado novo na VPS) ou **config.example.py**
4. **requirements.txt** - Dependências Python
5. **Dockerfile.telegram** - Dockerfile do container
6. **docker-compose.addition.yml** - Serviço para docker-compose
7. **README.md** - Documentação principal
8. **README_API.md** - Documentação da API
9. **GUIA_INSTALACAO_VPS.md** - Guia de instalação
10. **COMANDOS_VPS.txt** - Comandos prontos
11. **INSTALL.sh** - Script de instalação (opcional)
12. **.gitignore** - Arquivos a ignorar

## ❌ Arquivos NÃO enviar (já no .gitignore)

- `*.session` - Arquivos de sessão do Telegram
- `videos_baixados/` - Pasta com vídeos baixados
- `videos_baixados.json` - Controle de duplicatas
- `__pycache__/` - Cache Python
- `.env` - Variáveis de ambiente (sensíveis)
- `informacaoapp.text` - Informações sensíveis da API

## 🚀 Como Enviar (3 opções)

### Opção 1: Via GitHub Web Interface (MAIS FÁCIL)

1. Acesse: https://github.com/Rafael-Rangel/telegram
2. Clique em "Add file" → "Create new file"
3. Cole o conteúdo de cada arquivo
4. Salve (Commit changes)

### Opção 2: Instalar Git e usar linha de comando

```powershell
# Instalar Git para Windows
# Baixe de: https://git-scm.com/download/win

# Depois execute:
git init
git remote add origin https://github.com/Rafael-Rangel/telegram.git
git add api.py telegram_client.py config.py requirements.txt Dockerfile.telegram docker-compose.addition.yml README.md README_API.md GUIA_INSTALACAO_VPS.md COMANDOS_VPS.txt INSTALL.sh .gitignore
git commit -m "Initial commit: Telegram Video Downloader API"
git branch -M main
git push -u origin main
```

### Opção 3: GitHub Desktop (GUI)

1. Baixe: https://desktop.github.com/
2. Clone o repositório
3. Arraste os arquivos para a pasta
4. Commit e Push

## 📋 Checklist

- [ ] api.py
- [ ] telegram_client.py
- [ ] config.example.py (NÃO envie config.py!)
- [ ] requirements.txt
- [ ] Dockerfile.telegram
- [ ] docker-compose.addition.yml
- [ ] README.md
- [ ] README_API.md
- [ ] GUIA_INSTALACAO_VPS.md
- [ ] COMANDOS_VPS.txt
- [ ] INSTALL.sh
- [ ] .gitignore

