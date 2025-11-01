# 🎯 Guia Completo: Fluxo Diário no N8n

## 📋 Pré-requisitos

1. ✅ API modificada na VPS com os novos endpoints
2. ✅ Google Sheets configurado (coluna: `video_id`)
3. ✅ N8n com autenticação Google Sheets

---

## 🔄 Fluxo Completo (7 Passos)

### **PASSO 1: Buscar IDs Processados do Google Sheets**

**Nó:** `Google Sheets` → `Get Many`

- **Spreadsheet ID:** (ID da sua planilha)
- **Sheet Name:** (nome da aba)
- **Range:** `A:A` (coluna com video_id)

**Resultado:** Array com IDs já processados

---

### **PASSO 2: Processar Array de IDs**

**Nó:** `Set` ou `Code`

Extrair apenas os IDs (valores da coluna):

```javascript
// Se vier como array de objetos: [{ video_id: "..." }, ...]
{{ $json.map(item => item.video_id) }}

// Se vier como array simples: ["id1", "id2", ...]
{{ $json }}
```

---

### **PASSO 3: Baixar e Transcrever Vídeos Novos**

**Nó:** `HTTP Request`

**Method:** `POST`

**URL:** 
```
http://telegram-video-downloader:8000/download-videos
```

**Body (JSON):**
```json
{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true,
  "processed_ids": {{ $json }}
}
```

**Response esperada:**
```json
{
  "success": true,
  "videos": [...],
  "new_ids": ["id1", "id2", "id3"],
  "total": 3
}
```

---

### **PASSO 4: Salvar Transcrições no Google Drive**

**Nó:** `Split in Batches` ou `Loop Over Items`

Iterar sobre: `{{ $json.videos }}`

**Para cada vídeo:**

**Nó:** `Google Drive` → `Upload`

- **Filename:** `{{ $json.filename }}_transcricao.txt`
- **Content:** `{{ $json.transcription }}`
- **Folder:** (pasta de destino)

---

### **PASSO 5: Atualizar Google Sheets com Novos IDs**

**Nó:** `Google Sheets` → `Append`

- **Spreadsheet ID:** (mesmo da etapa 1)
- **Sheet Name:** (mesma aba)
- **Values:** 
  ```json
  [
    {
      "video_id": "{{ $json.videos[0].video_id }}",
      "date": "{{ $json.videos[0].date }}",
      "filename": "{{ $json.videos[0].filename }}"
    },
    {
      "video_id": "{{ $json.videos[1].video_id }}",
      "date": "{{ $json.videos[1].date }}",
      "filename": "{{ $json.videos[1].filename }}"
    },
    {
      "video_id": "{{ $json.videos[2].video_id }}",
      "date": "{{ $json.videos[2].date }}",
      "filename": "{{ $json.videos[2].filename }}"
    }
  ]
  ```

**Ou usar `Loop`** para adicionar cada um:

```javascript
{{ $json.videos.map(v => ({
  video_id: v.video_id,
  date: v.date,
  filename: v.filename
})) }}
```

---

### **PASSO 6: Limpar Vídeos da VPS**

**Nó:** `HTTP Request`

**Method:** `POST`

**URL:** 
```
http://telegram-video-downloader:8000/clean-videos
```

**Body (JSON):**

**Opção A - Limpar apenas os vídeos processados:**
```json
{
  "video_paths": {{ $json.videos.map(v => v.video_path) }}
}
```

**Opção B - Limpar tudo (mais simples):**
```json
{}
```

---

### **PASSO 7: Schedule (Agendar)**

**Nó:** `Schedule Trigger`

- **Trigger Times:** `0 8 * * *` (todo dia às 8h)
- Ou: `0 8 * * 1-5` (segunda a sexta às 8h)

---

## 📊 Estrutura da Planilha Google Sheets

| video_id | date | filename | size_mb |
|----------|------|----------|---------|
| -1002007723449_932_5179265096190264564 | 2025-10-24 | Thiago&Ju_Pre04.mp4 | 23.86 |
| -1002007723449_933_5179265096190264565 | 2025-10-24 | Rapunzel_Pre15.mp4 | 37.17 |

---

## 🎯 Workflow Simplificado (Versão Resumida)

```
1. Schedule (8h diária)
   ↓
2. Google Sheets → Get Many (IDs processados)
   ↓
3. Set → Extrair apenas valores
   ↓
4. HTTP Request → /download-videos (com processed_ids)
   ↓
5. Google Drive → Upload (transcrições)
   ↓
6. Google Sheets → Append (novos IDs)
   ↓
7. HTTP Request → /clean-videos (limpar VPS)
```

---

## ✅ Vantagens deste Fluxo

- ✅ **Zero duplicatas** - Consulta Google Sheets antes de baixar
- ✅ **Automático** - Roda sozinho todo dia às 8h
- ✅ **Transcrição incluída** - Texto vem direto na resposta
- ✅ **Limpeza automática** - VPS sempre limpa
- ✅ **Rastreável** - Google Sheets registra tudo
- ✅ **Escalável** - Fácil adicionar mais grupos

---

## 🐛 Troubleshooting

### Nenhum vídeo novo encontrado:
- Verifique se os IDs no Google Sheets estão corretos
- Verifique se há vídeos novos no grupo do Telegram

### Erro ao limpar:
- Verifique permissões do container
- Verifique se os caminhos estão corretos

### Transcrição falhando:
- Verifique logs: `docker logs telegram-video-downloader`
- Verifique se FFmpeg está instalado: `/health`

---

## 📝 Exemplo de Código n8n (Code Node)

Se precisar processar arrays, use um nó `Code`:

```javascript
// Extrair IDs processados
const processedIds = items.map(item => item.json.video_id);

// Retornar para próximo nó
return processedIds.map(id => ({ json: { processed_id: id } }));
```

---

## 🚀 Pronto para Produção!

Este fluxo está pronto para rodar automaticamente todos os dias. Ajuste os horários e parâmetros conforme necessário.

