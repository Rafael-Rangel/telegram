# 🎤 Como Usar o Endpoint de Transcrição

## 📋 Passo 1: Adicionar à API na VPS

### 1.1. Edite o api.py:

```bash
cd ~/telegram-downloader
nano api.py
```

### 1.2. Adicione o modelo Pydantic (procure por `class VideoResponse` e adicione depois):

```python
class TranscribeRequest(BaseModel):
    video_path: str
    video_id: Optional[str] = None
```

### 1.3. Adicione o endpoint (antes da linha `if __name__ == "__main__":`):

Copie todo o conteúdo do arquivo `endpoint_transcrever.py` que está neste repositório.

### 1.4. Reinicie o container:

```bash
cd ~
docker compose restart telegram-video-downloader
```

---

## 🎯 Passo 2: Usar no n8n

### Configuração do nó HTTP Request:

**Method:** `POST`

**URL:** 
```
http://telegram-video-downloader:8000/transcribe-video
```

**Send Body:**
- Marque como JSON

**Body (JSON):**
```json
{
  "video_path": "{{ $json.videos[0].video_path }}",
  "video_id": "{{ $json.videos[0].video_id }}"
}
```

Ou se você já tem o caminho do vídeo:
```json
{
  "video_path": "/tmp/telegram-videos/n1002007723449/2025-10-24/Thiago&Ju_Pre04.mp4",
  "video_id": "-1002007723449_932_5179265096190264564"
}
```

---

## 📤 Resposta Esperada:

```json
{
  "success": true,
  "transcription": "Texto completo transcrito do vídeo...",
  "transcription_path": "/tmp/telegram-videos/.../video_transcricao.txt",
  "video_path": "/tmp/telegram-videos/.../video.mp4",
  "video_id": "-1002007723449_932_5179265096190264564",
  "filename": "Thiago&Ju_Pre04.mp4",
  "message": "Vídeo transcrito com sucesso"
}
```

---

## 🔗 Workflow Completo no n8n:

1. **HTTP Request** - Baixar vídeos (sem transcrição):
   ```
   POST http://telegram-video-downloader:8000/download-videos
   ?grupo_id=-1002007723449&limite=3&transcrever=false
   ```

2. **Split in Batches** ou **Loop Over Items** - Para processar cada vídeo

3. **HTTP Request** - Transcrever cada vídeo:
   ```
   POST http://telegram-video-downloader:8000/transcribe-video
   Body: { "video_path": "{{ $json.video_path }}", "video_id": "{{ $json.video_id }}" }
   ```

4. **Usar a transcrição** - `{{ $json.transcription }}` contém o texto completo!

---

## ⚡ Dica:

Você também pode passar apenas o `video_path` sem o `video_id`. O endpoint vai gerar um ID automático baseado no caminho do arquivo.

