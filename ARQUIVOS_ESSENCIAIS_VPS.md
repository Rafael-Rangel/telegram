# 📦 Arquivos Essenciais para VPS

## ✅ ARQUIVOS NECESSÁRIOS (manter):

1. **api.py** - API principal
2. **telegram_client.py** - Funções do Telegram
3. **config.example.py** - Template de configuração
4. **requirements.txt** - Dependências Python
5. **Dockerfile.telegram** - Dockerfile do container
6. **README.md** - Documentação principal
7. **README_API.md** - Documentação da API
8. **PROXIMO_PASSO_VPS.md** - Guia de instalação (ou INSTRUCOES_VPS.md)

## ❌ ARQUIVOS DESNECESSÁRIOS (pode remover):

### Deploy em outros serviços (não usados no Docker):
- `app_gui.py`
- `app_web.py`
- `Procfile`
- `pyproject.toml`
- `railway.json`
- `runtime.txt`
- `uv.lock`
- `vercel.json`
- `templates/` (pasta)

### Documentação redundante (já usada):
- `ADICIONAR_AO_DOCKER_COMPOSE.yml` (já foi adicionado ao compose)
- `ARQUIVOS_PARA_GITHUB.md` (já enviado)
- `COMANDOS_VPS.txt`
- `COMANDOS_VPS_EXATOS.txt`
- `COMO_ENVIAR_GITHUB.md` (já enviado)
- `GUIA_INSTALACAO_VPS.md` (redundante)
- `INSTALL.sh` (não funciona no Docker)
- `RESUMO_UPLOAD.md` (já enviado)
- `docker-compose-final.yml` (referência, pode manter se quiser)

## 🧹 Comando para Limpar na VPS:

```bash
cd ~/telegram-downloader

# Remover arquivos desnecessários
rm -f app_gui.py app_web.py Procfile pyproject.toml railway.json runtime.txt uv.lock vercel.json
rm -rf templates/
rm -f ADICIONAR_AO_DOCKER_COMPOSE.yml ARQUIVOS_PARA_GITHUB.md COMANDOS_VPS.txt COMANDOS_VPS_EXATOS.txt
rm -f COMO_ENVIAR_GITHUB.md RESUMO_UPLOAD.md GUIA_INSTALACAO_VPS.md INSTALL.sh docker-compose-final.yml

# Verificar o que sobrou
ls -la
```

## 📋 Estrutura Final Ideal:

```
telegram-downloader/
├── api.py                    ✅ Essencial
├── telegram_client.py        ✅ Essencial
├── config.example.py         ✅ Essencial
├── requirements.txt          ✅ Essencial
├── Dockerfile.telegram       ✅ Essencial
├── README.md                 ✅ Documentação
├── README_API.md             ✅ Documentação
├── PROXIMO_PASSO_VPS.md      ✅ Guia (ou INSTRUCOES_VPS.md)
└── docker-compose.addition.yml (referência)
```

