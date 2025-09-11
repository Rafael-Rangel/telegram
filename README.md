# Text to Speech com Kokoro

Um aplicativo web moderno de conversão de texto para áudio usando a biblioteca Kokoro com geração em blocos e visualização em tempo real.

## ✨ Funcionalidades

- 🌐 **Interface Web Moderna** - Design responsivo e intuitivo
- 📝 **Geração em Blocos** - Divide o texto em parágrafos e gera áudio para cada um
- 🎵 **Visualização em Tempo Real** - Cards mostram o progresso de cada parágrafo
- 🎤 **Múltiplas Vozes** - pf_dora, pm_alex, pm_santa
- ▶️ **Reprodução Individual** - Ouça cada parágrafo separadamente
- 🔄 **Reprodução Sequencial** - Reproduz automaticamente o próximo parágrafo
- ⏯️ **Controles de Navegação** - Anterior, próximo, pausar, continuar, reiniciar
- 🎚️ **Controle de Velocidade** - Ajuste a velocidade de 0.5x a 2x
- 📊 **Barra de Progresso** - Acompanhe a geração em tempo real
- 💾 **Download Individual** - Baixe cada áudio separadamente
- 🎨 **Interface Responsiva** - Funciona em desktop e mobile

## 🚀 Como usar

### 1. Instalar dependências
```bash
uv sync
```

### 2. Executar a aplicação web
```bash
python app_web.py
```

### 3. Acessar no navegador
Abra: http://localhost:5000

### 4. Usar o aplicativo
1. Digite o texto (use parágrafos separados por linhas em branco)
2. Selecione a voz desejada
3. Clique em "Gerar Áudio"
4. Acompanhe o progresso nos cards da lateral
5. Use os controles de reprodução:
   - **Reproduzir Tudo**: Toca todos os parágrafos sequencialmente
   - **Navegação**: Anterior, próximo, pausar, continuar
   - **Velocidade**: Ajuste de 0.5x a 2x com slider e presets
   - **Cards clicáveis**: Clique em qualquer card para reproduzir

## 📁 Arquivos do projeto

- `app_web.py` - Aplicação web Flask principal
- `templates/index.html` - Interface web moderna
- `app_gui.py` - Interface gráfica desktop (versão anterior)
- `app.py` - Script simples (versão anterior)
- `pyproject.toml` - Configurações e dependências

## 🎤 Vozes disponíveis

- **pf_dora** - Dora (Feminina)
- **pm_alex** - Alex (Masculina)  
- **pm_santa** - Santa (Masculina)

## 💻 Requisitos

- Python 3.12+
- Bibliotecas: kokoro, numpy, soundfile, flask

## 📖 Exemplo de uso

1. Abra http://localhost:5000
2. Digite um texto com parágrafos:
   ```
   Este é o primeiro parágrafo.
   
   Este é o segundo parágrafo.
   
   E assim por diante...
   ```
3. Selecione a voz "Alex"
4. Clique em "Gerar Áudio"
5. Acompanhe o progresso nos cards
6. Reproduza cada parágrafo quando estiver pronto

## 🔧 Solução de problemas

- **Erro de inicialização**: Aguarde alguns segundos para o pipeline carregar
- **Áudio não gera**: Verifique se o texto não está vazio
- **Cards não aparecem**: Verifique se o texto tem parágrafos separados
- **Erro de conexão**: Verifique se a porta 5000 está livre
