# 🎤 Endpoint para Transcrever Vídeos

## 📋 O que faz:

- Recebe o caminho do vídeo ou ID do vídeo
- Transcreve usando Whisper
- Retorna o texto transcrito + ID do vídeo

## Como adicionar à API existente

Adicione este endpoint ao seu `api.py` na VPS (copie do arquivo `endpoint_transcrever.py`):

```python
@app.post("/transcribe-video")
async def transcribe_video(video_path: str):
    """
    Transcreve um vídeo já baixado usando Whisper
    
    Args:
        video_path: Caminho completo do vídeo (ex: /tmp/telegram-videos/.../video.mp4)
    
    Returns:
        Transcrição do vídeo em texto
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail="Vídeo não encontrado")
        
        # Verificar FFmpeg
        if not verificar_ffmpeg():
            raise HTTPException(status_code=500, detail="FFmpeg não está instalado")
        
        # Verificar Whisper
        if not WHISPER_DISPONIVEL:
            raise HTTPException(status_code=500, detail="Whisper não está disponível")
        
        # Transcrever o vídeo
        texto, caminho_txt = transcrever_video(video_path)
        
        if texto and caminho_txt:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "transcription": texto,
                    "transcription_path": caminho_txt,
                    "video_path": video_path,
                    "message": "Vídeo transcrito com sucesso"
                }
            )
        else:
            raise HTTPException(status_code=500, detail="Erro ao transcrever vídeo")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
```

## Como usar no n8n:

### Método 1: Transcrever vídeo já baixado (NOVO ENDPOINT)

**URL:** `http://telegram-video-downloader:8000/transcribe-video`

**Method:** `POST`

**Query Parameters:**
| Name | Value |
|------|-------|
| `video_path` | `/tmp/telegram-videos/n1002007723449/2025-10-24/Thiago&Ju_Pre04.mp4` |
| `video_id` | `-1002007723449_932_5179265096190264564` (opcional) |

**Ou via Body (JSON):**
```json
{
  "video_path": "/tmp/telegram-videos/n1002007723449/2025-10-24/Thiago&Ju_Pre04.mp4",
  "video_id": "-1002007723449_932_5179265096190264564"
}
```

### Método 2: Transcrever durante o download (endpoint existente)
```http
POST http://telegram-video-downloader:8000/download-videos?grupo_id=-1002007723449&limite=3&transcrever=true
```

## Resposta do endpoint:

```json
{
  "success": true,
  "transcription": "Texto transcrito do vídeo aqui...",
  "transcription_path": "/tmp/telegram-videos/.../video_transcricao.txt",
  "video_path": "/tmp/telegram-videos/.../video.mp4",
  "video_id": "-1002007723449_932_5179265096190264564",
  "filename": "Thiago&Ju_Pre04.mp4",
  "message": "Vídeo transcrito com sucesso"
}
```

## Como adicionar na VPS:

1. Edite o `api.py`:
```bash
cd ~/telegram-downloader
nano api.py
```

2. Adicione o endpoint antes da linha `if __name__ == "__main__":`

3. Reinicie o container:
```bash
cd ~
docker compose restart telegram-video-downloader
```

4. Teste:
```bash
curl -X POST "http://localhost:8001/transcribe-video?video_path=/tmp/telegram-videos/n1002007723449/2025-10-24/Thiago&Ju_Pre04.mp4"
```

