"""
Endpoint para adicionar ao api.py - Rota de Transcrição de Vídeos
Adicione este código ANTES da linha: if __name__ == "__main__":

IMPORTANTE: Adicione também este modelo Pydantic no início do arquivo (junto com VideoResponse):
"""

class TranscribeRequest(BaseModel):
    video_path: str
    video_id: Optional[str] = None


@app.post("/transcribe-video")
async def transcribe_video(request: TranscribeRequest):
    """
    Transcreve um vídeo já baixado usando Whisper
    
    Args:
        request: Objeto com video_path (obrigatório) e video_id (opcional)
    
    Returns:
        Texto transcrito + ID do vídeo
    """
    try:
        video_path = request.video_path
        video_id = request.video_id
        
        # Verificar se o arquivo existe
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail=f"Vídeo não encontrado: {video_path}")
        
        # Verificar extensão do arquivo
        if not video_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv')):
            raise HTTPException(status_code=400, detail="Arquivo deve ser um vídeo")
        
        # Verificar FFmpeg
        if not verificar_ffmpeg():
            raise HTTPException(status_code=500, detail="FFmpeg não está instalado")
        
        # Verificar Whisper
        if not WHISPER_DISPONIVEL:
            raise HTTPException(status_code=500, detail="Whisper não está disponível")
        
        print(f"🎤 Transcrevendo vídeo: {video_path}")
        
        # Transcrever o vídeo
        texto, caminho_txt = transcrever_video(video_path)
        
        if not texto or not caminho_txt:
            raise HTTPException(status_code=500, detail="Erro ao transcrever vídeo. Verifique os logs.")
        
        # Extrair nome do arquivo
        filename = os.path.basename(video_path)
        
        # Se video_id não foi fornecido, gerar um hash do caminho
        if not video_id:
            import hashlib
            video_id = hashlib.md5(video_path.encode()).hexdigest()[:16]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "transcription": texto,
                "transcription_path": caminho_txt,
                "video_path": video_path,
                "video_id": video_id,
                "filename": filename,
                "message": "Vídeo transcrito com sucesso"
            }
        )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao transcrever: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

