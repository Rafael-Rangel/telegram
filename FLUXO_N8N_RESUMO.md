# 🎯 Resumo Rápido: Fluxo n8n

## 📋 Lista de Nós (8 nós)

1. **Schedule Trigger** - Agendar execução diária
2. **Google Sheets** - Buscar IDs processados  
3. **Code** - Processar array de IDs
4. **HTTP Request** - Baixar vídeos novos
5. **Google Drive** - Salvar transcrições
6. **Google Sheets** - Adicionar novos IDs
7. **HTTP Request** - Limpar VPS
8. **IF** (opcional) - Tratamento de erros

---

## 🔧 Configuração Rápida de Cada Nó

### 1️⃣ Schedule Trigger
```
Trigger Times: 0 8 * * *
```

### 2️⃣ Google Sheets (Get Many)
```
Operation: Get Many
Range: A:A
Return All: true
```

### 3️⃣ Code (Processar IDs)
```javascript
const processedIds = $input.all().map(item => item.json.video_id || item.json);
return [{ json: { processed_ids: processedIds } }];
```

### 4️⃣ HTTP Request (download-videos)
```
Method: POST
URL: http://telegram-video-downloader:8000/download-videos
Body:
{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true,
  "processed_ids": {{ $json.processed_ids }}
}
```

### 5️⃣ Google Drive (Upload)
```
Operation: Upload
File Name: {{ $json.filename }}_transcricao.txt
File Content: {{ $json.transcription }}
```

### 6️⃣ Google Sheets (Append)
```
Operation: Append
Values: 
[
  {
    "video_id": "{{ $json.video_id }}",
    "date": "{{ $json.date }}",
    "filename": "{{ $json.filename }}"
  }
]
```

### 7️⃣ HTTP Request (clean-videos)
```
Method: POST
URL: http://telegram-video-downloader:8000/clean-videos
Body: {}
```

---

## 🔗 Ordem de Conexão

```
[Schedule] → [Sheets Get] → [Code] → [HTTP Download]
                                              ↓
                                        [Split/Loop?]
                                              ↓
                                    [Drive Upload] + [Sheets Append]
                                              ↓
                                          [HTTP Clean]
```

---

## ⚡ Expressões Úteis n8n

### Verificar sucesso:
```javascript
{{ $json.success === true }}
```

### Contar vídeos:
```javascript
{{ $json.videos.length }}
```

### Extrair apenas IDs:
```javascript
{{ $json.new_ids }}
```

### Formatar para Sheets:
```javascript
{{ $json.videos.map(v => ({
  video_id: v.video_id,
  date: v.date,
  filename: v.filename
})) }}
```

---

## 🎯 Fluxo Mínimo (5 nós)

Se quiser simplificar ainda mais:

1. **Schedule** → Dispara às 8h
2. **Google Sheets** → Busca IDs
3. **HTTP Request** → Baixa vídeos (com transcrever=true)
4. **Google Sheets** → Adiciona novos IDs (usa `new_ids`)
5. **HTTP Request** → Limpa VPS

**Nota:** Pule o Google Drive se não precisar salvar transcrições separadamente (já vem na resposta).

---

## ✅ Teste Rápido

1. Execute o workflow manualmente
2. Verifique logs de cada nó
3. Confirme que vídeos foram baixados
4. Verifique Google Sheets atualizado
5. Confirme que VPS foi limpa

---

**Documentação completa:** Veja `GUIA_FLUXO_N8N_COMPLETO.md`

