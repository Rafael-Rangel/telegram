# 🔄 Fluxo Diário Completo - API Modificada

## 📋 Modificações Necessárias na API

### 1. Modelos Pydantic (adicionar no início do arquivo, junto com `VideoResponse`):

```python
class DownloadVideosRequest(BaseModel):
    grupo_id: str
    limite: int = 3
    transcrever: bool = True
    processed_ids: Optional[List[str]] = []  # Lista de IDs já processados (do Google Sheets)

class CleanVideosRequest(BaseModel):
    video_paths: Optional[List[str]] = None  # Lista específica, ou None para limpar tudo
```

### 2. Modificar endpoint `/download-videos`:

O endpoint deve:
- Aceitar `processed_ids` do body (JSON)
- Ignorar vídeos cujos IDs estão na lista
- Transcrever automaticamente se `transcrever=true`
- Retornar apenas IDs dos novos vídeos

### 3. Novo endpoint `/clean-videos`:

Para limpar os arquivos após processamento.

---

## 📝 Código Completo

Ver arquivo: `endpoints_fluxo_diario.py`

---

## 🎯 Como Funciona:

### Endpoint `/download-videos` (MODIFICADO):

**Request:**
```json
{
  "grupo_id": "-1002007723449",
  "limite": 3,
  "transcrever": true,
  "processed_ids": [
    "-1002007723449_932_5179265096190264564",
    "-1002007723449_933_5179265096190264565"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "3 vídeo(s) baixado(s) e transcrito(s) com sucesso",
  "videos": [
    {
      "success": true,
      "video_path": "/tmp/telegram-videos/.../video1.mp4",
      "transcription_path": "/tmp/telegram-videos/.../video1_transcricao.txt",
      "transcription": "Texto completo transcrito...",
      "video_id": "-1002007723449_934_5179265096190264566",
      "date": "2025-11-01",
      "filename": "video1.mp4",
      "size_mb": 25.5
    }
  ],
  "new_ids": [
    "-1002007723449_934_5179265096190264566",
    "-1002007723449_935_5179265096190264567",
    "-1002007723449_936_5179265096190264568"
  ],
  "total": 3
}
```

### Endpoint `/clean-videos` (NOVO):

**Request:**
```json
{
  "video_paths": [
    "/tmp/telegram-videos/.../video1.mp4",
    "/tmp/telegram-videos/.../video2.mp4"
  ]
}
```

Ou limpar tudo (sem especificar):
```json
{}
```

**Response:**
```json
{
  "success": true,
  "cleaned": 5,
  "message": "5 arquivo(s) removido(s) com sucesso"
}
```

---

## 🔄 Fluxo no N8n:

1. **Buscar IDs processados do Google Sheets**
2. **Chamar `/download-videos`** com a lista de IDs
3. **Salvar transcrições no Drive**
4. **Atualizar Google Sheets** com novos IDs
5. **Chamar `/clean-videos`** para limpar a VPS

---

## ✅ Vantagens:

- ✅ Não baixa duplicatas (usa lista do Google Sheets)
- ✅ Transcreve automaticamente
- ✅ Retorna apenas IDs novos (fácil de atualizar no Sheets)
- ✅ Limpa automaticamente após processamento
- ✅ Pronto para automação diária

