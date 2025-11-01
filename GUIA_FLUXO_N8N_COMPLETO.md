# 🎯 Guia Completo: Montar Fluxo no n8n

## 📋 Visão Geral do Fluxo

```
1. Schedule Trigger (8h diária)
   ↓
2. Google Sheets → Buscar IDs processados
   ↓
3. Code/Set → Processar array de IDs
   ↓
4. HTTP Request → Baixar e transcrever vídeos
   ↓
5. Split in Batches → Iterar sobre vídeos
   ↓
6. Google Drive → Salvar transcrições
   ↓
7. Google Sheets → Adicionar novos IDs
   ↓
8. HTTP Request → Limpar VPS
```

---

## 🔧 PASSO 1: Schedule Trigger

**Nó:** `Schedule Trigger`

**Configurações:**
- **Trigger Times:** `0 8 * * *` (todo dia às 8h)
- Ou: `0 8 * * 1-5` (segunda a sexta às 8h)

**Saída:** Dispara o workflow

---

## 📊 PASSO 2: Buscar IDs do Google Sheets

**Nó:** `Google Sheets` → `Get Many`

**Configurações:**

**Credential:** Configure autenticação Google Sheets

**Operation:** `Get Many`

**Spreadsheet ID:** 
- Pegue da URL: `https://docs.google.com/spreadsheets/d/[ESTE_ID]/edit`
- Exemplo: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

**Sheet Name:** Nome da aba (ex: `Sheet1`)

**Range:** `A:A` (assumindo que `video_id` está na coluna A)

**Output Options:**
- **Return All:** `true`

**Saída esperada:**
```json
[
  { "video_id": "-1002007723449_932_5179265096190264564" },
  { "video_id": "-1002007723449_933_5179265096190264565" }
]
```

---

## 🔄 PASSO 3: Processar Array de IDs

**Nó:** `Code` (ou `Set`)

**Opção A - Usando Code:**

**Language:** JavaScript

**Code:**
```javascript
// Extrair apenas os valores de video_id
const processedIds = $input.all().map(item => {
  // Se vier como objeto: { video_id: "..." }
  if (item.json.video_id) {
    return item.json.video_id;
  }
  // Se vier direto como string
  return item.json;
});

// Retornar como objeto para o próximo nó
return [{
  json: {
    processed_ids: processedIds
  }
}];
```

**Opção B - Usando Set:**

**Keep Only Set Fields:** `false`

**Fields to Set:**
- **Name:** `processed_ids`
- **Value:** `{{ $json.video_id }}`

**Ou se vier direto:**
- **Value:** `{{ $json }}`

---

## 📥 PASSO 4: Baixar e Transcrever Vídeos

**Nó:** `HTTP Request`

**Configurações:**

**Method:** `POST`

**URL:** 
```
http://telegram-video-downloader:8000/download-videos
```

**Authentication:** `None`

**Send Body:** `true`

**Content Type:** `JSON`

**Body (JSON):**
```json
{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true,
  "processed_ids": {{ $json.processed_ids }}
}
```

**Ou usando expressão n8n:**
```javascript
{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true,
  "processed_ids": {{ JSON.stringify($json.processed_ids) }}
}
```

**Saída esperada:**
```json
{
  "success": true,
  "videos": [
    {
      "video_id": "novo_id_1",
      "transcription": "Texto transcrito...",
      "video_path": "/tmp/telegram-videos/.../video1.mp4",
      "filename": "video1.mp4",
      "date": "2025-11-01",
      "size_mb": 25.5
    }
  ],
  "new_ids": ["novo_id_1", "novo_id_2", "novo_id_3"]
}
```

---

## 🔀 PASSO 5: Separar Vídeos (Opcional)

**Nó:** `Split in Batches` ou `Loop Over Items`

**Configurações:**

**Batch Size:** `1`

**Ou usar `Loop Over Items`** para processar cada vídeo individualmente.

**Iterate Over:** `{{ $json.videos }}`

---

## 💾 PASSO 6: Salvar Transcrições no Google Drive

**Nó:** `Google Drive` → `Upload`

**Configurações:**

**Credential:** Configure autenticação Google Drive

**Operation:** `Upload`

**File Name:** 
```
{{ $json.filename }}_transcricao.txt
```

**Binary Data:** `false`

**File Content:**
```
{{ $json.transcription }}
```

**Parent Folder ID:** (opcional - ID da pasta de destino)

**Ou usar `Set` para formatar primeiro:**

**Nó:** `Set` (antes do Google Drive)

**Fields:**
- **Name:** `fileName`
- **Value:** `{{ $json.filename.replace('.mp4', '_transcricao.txt').replace('.avi', '_transcricao.txt') }}`
- **Name:** `fileContent`
- **Value:** `{{ $json.transcription }}`

---

## 📝 PASSO 7: Atualizar Google Sheets com Novos IDs

**Nó:** `Google Sheets` → `Append`

**Configurações:**

**Spreadsheet ID:** (mesmo do Passo 2)

**Sheet Name:** (mesma aba)

**Columns:** 
- `video_id`
- `date`
- `filename`
- `size_mb`

**Values:** 

**Opção A - Adicionar todos de uma vez:**

Usar um nó `Code` antes para formatar:

```javascript
// Formatar dados dos vídeos para o Google Sheets
const videos = $input.first().json.videos;

return videos.map(video => ({
  json: {
    video_id: video.video_id,
    date: video.date,
    filename: video.filename,
    size_mb: video.size_mb
  }
}));
```

**Opção B - Adicionar cada um separadamente:**

Usar `Split in Batches` e adicionar um por um:

**Values:**
```json
[
  {
    "video_id": "{{ $json.video_id }}",
    "date": "{{ $json.date }}",
    "filename": "{{ $json.filename }}",
    "size_mb": "{{ $json.size_mb }}"
  }
]
```

---

## 🧹 PASSO 8: Limpar VPS

**Nó:** `HTTP Request`

**Configurações:**

**Method:** `POST`

**URL:** 
```
http://telegram-video-downloader:8000/clean-videos
```

**Authentication:** `None`

**Send Body:** `true`

**Content Type:** `JSON`

**Body (JSON):**

**Opção A - Limpar apenas vídeos processados:**
```json
{
  "video_paths": {{ JSON.stringify($('HTTP Request').all().map(item => item.json.videos.map(v => v.video_path)).flat()) }}
}
```

**Opção B - Limpar tudo (mais simples):**
```json
{}
```

**Saída esperada:**
```json
{
  "success": true,
  "cleaned": 5,
  "message": "5 arquivo(s) removido(s) com sucesso"
}
```

---

## 📊 Estrutura da Planilha Google Sheets

### Colunas Recomendadas:

| video_id | date | filename | size_mb | transcription_saved |
|----------|------|----------|---------|---------------------|
| -1002007723449_932_5179265096190264564 | 2025-10-24 | Thiago&Ju_Pre04.mp4 | 23.86 | true |
| -1002007723449_933_5179265096190264565 | 2025-10-24 | Rapunzel_Pre15.mp4 | 37.17 | true |

**Nota:** A coluna `video_id` deve estar na coluna A para o `Range: A:A` funcionar.

---

## 🔗 Como Conectar os Nós

```
Schedule Trigger
    ↓
Google Sheets (Get Many)
    ↓
Code (Processar IDs)
    ↓
HTTP Request (download-videos)
    ↓
┌─────────────────┬──────────────────┬─────────────────┐
│                 │                  │                 │
Split in Batches  │  (opcional)     │  (opcional)     │
│                 │                  │                 │
    ↓                                 │                 │
Google Drive                          │                 │
(Upload)                              │                 │
    ↓                                 │                 │
Google Sheets ←──────────────────────┘                 │
(Append)                                                  │
    ↓                                                      │
HTTP Request ←───────────────────────────────────────────┘
(clean-videos)
```

**Versão Simplificada (sem Split):**

```
Schedule Trigger
    ↓
Google Sheets (Get Many)
    ↓
Code (Processar IDs)
    ↓
HTTP Request (download-videos)
    ↓
Code (Formatar para Sheets)
    ↓
Google Sheets (Append) ──→ Google Drive (Upload múltiplos)
    ↓
HTTP Request (clean-videos)
```

---

## 💡 Dicas Importantes

### 1. Tratamento de Erros

Adicione nó `IF` após cada operação crítica:

```javascript
// Verificar se download foi bem-sucedido
{{ $json.success === true }}
```

### 2. Logs e Debug

Use `Code` para logar dados:

```javascript
console.log('IDs processados:', $json.processed_ids);
console.log('Vídeos baixados:', $json.videos.length);
return $input.all();
```

### 3. Validação de Dados

Verificar se há vídeos antes de processar:

```javascript
{{ $json.videos && $json.videos.length > 0 }}
```

### 4. Timeout

Configurar timeout maior para transcrição (pode levar minutos):

**No nó HTTP Request:**
- **Options:** `Request Timeout` → `600000` (10 minutos)

---

## ✅ Checklist Final

- [ ] Schedule configurado para 8h
- [ ] Google Sheets conectado e testado
- [ ] Array de IDs sendo processado corretamente
- [ ] HTTP Request retornando vídeos
- [ ] Transcrições sendo salvas no Drive
- [ ] Novos IDs sendo adicionados ao Sheets
- [ ] VPS sendo limpa após processamento
- [ ] Tratamento de erros implementado
- [ ] Logs configurados para debug

---

## 🐛 Troubleshooting

### Erro: "processed_ids is not iterable"
**Solução:** Verificar se o array está sendo passado corretamente no body JSON.

### Erro: "No videos found"
**Solução:** Verificar se os IDs no Google Sheets estão no formato correto.

### Erro: Timeout na transcrição
**Solução:** Aumentar timeout do HTTP Request para 600000ms (10 minutos).

### Erro: Google Sheets append falha
**Solução:** Verificar permissões da conta Google e formato dos dados.

---

## 🚀 Pronto para Produção!

Siga este guia passo a passo e seu fluxo estará funcionando automaticamente todos os dias às 8h!

