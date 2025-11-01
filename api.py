"""
API FastAPI para baixar vídeos do Telegram e integrar com n8n
"""
import os
import json
import subprocess
import hashlib
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from telethon import TelegramClient

# Configurações do Telegram (pode vir de variáveis de ambiente)
API_ID = int(os.getenv("TELEGRAM_API_ID", "29090427"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "88bf96af8dc0652c6f5026417b7d8f25")
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_session")

app = FastAPI(title="Telegram Video Downloader API")

# Pasta base para salvar vídeos (dentro do container, será montado em /tmp)
BASE_FOLDER = "/tmp/telegram-videos"
os.makedirs(BASE_FOLDER, exist_ok=True)

# Arquivo de controle
CONTROLE_BAIXADOS = os.path.join(BASE_FOLDER, "videos_baixados.json")

# Cliente Telegram global
client = None

# Importar Whisper para transcrição (opcional)
try:
    import whisper
    WHISPER_DISPONIVEL = True
except ImportError:
    WHISPER_DISPONIVEL = False


# Modelos Pydantic
class DownloadVideosRequest(BaseModel):
    grupo_id: str
    limite: int = 3
    transcrever: bool = True
    processed_ids: Optional[List[str]] = []

class CleanVideosRequest(BaseModel):
    video_paths: Optional[List[str]] = None

class TranscribeRequest(BaseModel):
    video_path: str
    video_id: Optional[str] = None


def verificar_ffmpeg():
    """Verifica se o FFmpeg está instalado"""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


def carregar_videos_baixados():
    """Carrega a lista de vídeos já baixados"""
    if os.path.exists(CONTROLE_BAIXADOS):
        try:
            with open(CONTROLE_BAIXADOS, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except:
            return set()
    return set()


def salvar_video_baixado(video_id):
    """Salva o ID de um vídeo baixado"""
    videos_baixados = carregar_videos_baixados()
    videos_baixados.add(video_id)
    with open(CONTROLE_BAIXADOS, "w", encoding="utf-8") as f:
        json.dump(list(videos_baixados), f, indent=2)


def verificar_se_ja_baixado(message):
    """Verifica se um vídeo já foi baixado"""
    videos_baixados = carregar_videos_baixados()
    
    # Criar ID único
    chat_id = None
    if hasattr(message, 'chat_id'):
        chat_id = message.chat_id
    elif hasattr(message, 'peer_id'):
        chat_id = message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else message.peer_id
    
    message_id = message.id
    file_id = None
    
    if message.video:
        file_id = message.video.id if hasattr(message.video, 'id') else None
    elif message.media and hasattr(message.media, 'document'):
        if hasattr(message.media.document, 'id'):
            file_id = message.media.document.id
    
    if file_id:
        video_id = f"{chat_id}_{message_id}_{file_id}"
    else:
        video_id = f"{chat_id}_{message_id}"
    
    return video_id in videos_baixados, video_id


def transcrever_video(caminho_video):
    """Transcreve um vídeo usando Whisper"""
    if not WHISPER_DISPONIVEL:
        return None, None
    
    if not verificar_ffmpeg():
        return None, None
    
    try:
        model = whisper.load_model("base")
        resultado = model.transcribe(caminho_video, language="pt")
        texto_transcrito = resultado["text"].strip()
        
        caminho_txt = os.path.splitext(caminho_video)[0] + "_transcricao.txt"
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(texto_transcrito)
        
        return texto_transcrito, caminho_txt
    except Exception as e:
        print(f"❌ Erro ao transcrever: {e}")
        return None, None


async def get_telegram_client():
    """Obtém ou cria o cliente Telegram"""
    global client
    if client is None or (hasattr(client, 'is_connected') and not client.is_connected()):
        # Usar caminho completo para a sessão (montado como volume)
        session_path = f"/app/.telegram_session/{SESSION_NAME}"
        client = TelegramClient(session_path, API_ID, API_HASH)
        await client.start()
    return client


@app.on_event("startup")
async def startup_event():
    """Inicializa o cliente Telegram ao iniciar"""
    try:
        await get_telegram_client()
        print("✅ Cliente Telegram conectado!")
    except Exception as e:
        print(f"⚠️ Erro ao conectar Telegram: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Desconecta o cliente Telegram ao encerrar"""
    global client
    if client:
        await client.disconnect()


@app.get("/health")
async def health():
    """Endpoint de saúde"""
    return {
        "status": "ok",
        "ffmpeg": verificar_ffmpeg(),
        "whisper": WHISPER_DISPONIVEL
    }


@app.post("/download-videos")
async def download_videos(request: DownloadVideosRequest):
    """
    Baixa vídeos de um grupo do Telegram (MODIFICADO PARA FLUXO DIÁRIO)
    
    Args:
        request: Objeto com grupo_id, limite, transcrever e processed_ids
    
    Returns:
        Lista de vídeos baixados com transcrição + lista de IDs novos
    """
    try:
        telegram_client = await get_telegram_client()
        
        # Converter grupo_id para int
        try:
            grupo_id_int = int(request.grupo_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="grupo_id deve ser um número")
        
        # Converter processed_ids para set para busca rápida
        processed_ids_set = set(request.processed_ids) if request.processed_ids else set()
        
        # Obter entidade do grupo
        try:
            grupo_entity = await telegram_client.get_entity(grupo_id_int)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Grupo não encontrado: {str(e)}")
        
        grupo_nome = grupo_entity.title if hasattr(grupo_entity, 'title') else str(request.grupo_id)
        
        # Criar pasta do grupo
        pasta_grupo = os.path.join(BASE_FOLDER, str(grupo_id_int).replace('-', 'n'))
        os.makedirs(pasta_grupo, exist_ok=True)
        
        videos_baixados_list = []
        videos_encontrados = 0
        
        print(f"🔍 Procurando até {request.limite} vídeos NOVOS no grupo: {grupo_nome}")
        print(f"📋 IDs já processados: {len(processed_ids_set)} vídeo(s)")
        
        # Buscar mensagens do grupo
        async for message in telegram_client.iter_messages(grupo_entity, limit=1000):
            if len(videos_baixados_list) >= request.limite:
                break
            
            # Verificar se a mensagem tem vídeo
            tem_video = False
            if message.video:
                tem_video = True
            elif message.media and hasattr(message.media, 'document'):
                doc = message.media.document
                if doc and hasattr(doc, 'mime_type') and doc.mime_type and 'video' in doc.mime_type:
                    tem_video = True
            
            if tem_video:
                videos_encontrados += 1
                
                # Gerar ID único do vídeo (mesmo método usado antes)
                chat_id = None
                if hasattr(message, 'chat_id'):
                    chat_id = message.chat_id
                elif hasattr(message, 'peer_id'):
                    chat_id = message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else message.peer_id
                
                message_id = message.id
                file_id = None
                
                if message.video:
                    file_id = message.video.id if hasattr(message.video, 'id') else None
                elif message.media and hasattr(message.media, 'document'):
                    if hasattr(message.media.document, 'id'):
                        file_id = message.media.document.id
                
                if file_id:
                    video_id = f"{chat_id}_{message_id}_{file_id}"
                else:
                    video_id = f"{chat_id}_{message_id}"
                
                # VERIFICAR SE JÁ FOI PROCESSADO (nova lógica)
                if video_id in processed_ids_set:
                    print(f"⏭️ Vídeo {videos_encontrados} já processado (ID: {video_id}) - pulando")
                    continue
                
                print(f"📹 Processando vídeo novo {videos_encontrados} (ID: {video_id})...")
                
                # Data da mensagem
                data_msg = message.date.strftime("%Y-%m-%d") if message.date else datetime.now().strftime("%Y-%m-%d")
                pasta_data = os.path.join(pasta_grupo, data_msg)
                os.makedirs(pasta_data, exist_ok=True)
                
                # Baixar o vídeo
                try:
                    nome_arquivo = await telegram_client.download_media(
                        message,
                        file=pasta_data
                    )
                    
                    if nome_arquivo:
                        tamanho = os.path.getsize(nome_arquivo) / (1024 * 1024)  # MB
                        filename = os.path.basename(nome_arquivo)
                        
                        # Transcrever se solicitado
                        transcription_path = None
                        transcription_text = None
                        if request.transcrever and verificar_ffmpeg():
                            try:
                                texto, caminho_txt = transcrever_video(nome_arquivo)
                                if caminho_txt:
                                    transcription_path = caminho_txt
                                    transcription_text = texto
                            except Exception as e:
                                print(f"⚠️ Erro ao transcrever: {e}")
                        
                        # Adicionar à lista de resultados
                        videos_baixados_list.append({
                            "success": True,
                            "video_path": nome_arquivo,
                            "transcription_path": transcription_path,
                            "transcription": transcription_text,
                            "video_id": video_id,
                            "date": data_msg,
                            "filename": filename,
                            "size_mb": round(tamanho, 2),
                            "message": f"Vídeo baixado e transcrito com sucesso: {filename}"
                        })
                        
                        print(f"✅ Vídeo processado: {filename} ({tamanho:.2f} MB)")
                    else:
                        print(f"⚠️ Erro ao baixar vídeo {videos_encontrados}")
                        
                except Exception as e:
                    print(f"❌ Erro ao processar vídeo: {e}")
                    continue
        
        if not videos_baixados_list:
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Nenhum vídeo novo encontrado",
                    "videos": [],
                    "new_ids": [],
                    "total": 0
                }
            )
        
        # Extrair apenas os IDs dos novos vídeos
        new_ids = [v["video_id"] for v in videos_baixados_list]
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"{len(videos_baixados_list)} vídeo(s) baixado(s) e transcrito(s) com sucesso",
                "videos": videos_baixados_list,
                "new_ids": new_ids,  # Lista apenas dos IDs novos (para atualizar Google Sheets)
                "total": len(videos_baixados_list)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.post("/transcribe-video")
async def transcribe_video(request: TranscribeRequest):
    """Transcreve um vídeo já baixado usando Whisper"""
    try:
        video_path = request.video_path
        video_id = request.video_id
        
        if not os.path.exists(video_path):
            raise HTTPException(status_code=404, detail=f"Vídeo não encontrado: {video_path}")
        
        if not video_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv')):
            raise HTTPException(status_code=400, detail="Arquivo deve ser um vídeo")
        
        if not verificar_ffmpeg():
            raise HTTPException(status_code=500, detail="FFmpeg não está instalado")
        
        if not WHISPER_DISPONIVEL:
            raise HTTPException(status_code=500, detail="Whisper não está disponível")
        
        print(f"🎤 Transcrevendo vídeo: {video_path}")
        
        texto, caminho_txt = transcrever_video(video_path)
        
        if not texto or not caminho_txt:
            raise HTTPException(status_code=500, detail="Erro ao transcrever vídeo. Verifique os logs.")
        
        filename = os.path.basename(video_path)
        
        if not video_id:
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


@app.post("/clean-videos")
async def clean_videos(request: CleanVideosRequest = CleanVideosRequest()):
    """Limpa arquivos de vídeo da VPS após processamento"""
    try:
        cleaned_count = 0
        
        if request.video_paths:
            # Limpar apenas arquivos específicos
            print(f"🧹 Limpando {len(request.video_paths)} arquivo(s) específico(s)...")
            for video_path in request.video_paths:
                try:
                    if os.path.exists(video_path):
                        # Remover vídeo
                        os.remove(video_path)
                        cleaned_count += 1
                        print(f"✅ Removido: {video_path}")
                        
                        # Tentar remover transcrição também (se existir)
                        transcription_path = os.path.splitext(video_path)[0] + "_transcricao.txt"
                        if os.path.exists(transcription_path):
                            os.remove(transcription_path)
                            cleaned_count += 1
                except Exception as e:
                    print(f"⚠️ Erro ao remover {video_path}: {e}")
        else:
            # Limpar toda a pasta /tmp/telegram-videos (exceto videos_baixados.json)
            print("🧹 Limpando todos os vídeos da pasta...")
            if os.path.exists(BASE_FOLDER):
                for root, dirs, files in os.walk(BASE_FOLDER):
                    for file in files:
                        if file != "videos_baixados.json":  # Preservar controle
                            file_path = os.path.join(root, file)
                            try:
                                os.remove(file_path)
                                cleaned_count += 1
                            except Exception as e:
                                print(f"⚠️ Erro ao remover {file_path}: {e}")
                
                # Remover pastas vazias (exceto BASE_FOLDER)
                for root, dirs, files in os.walk(BASE_FOLDER, topdown=False):
                    if root != BASE_FOLDER and not os.listdir(root):
                        try:
                            os.rmdir(root)
                        except:
                            pass
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "cleaned": cleaned_count,
                "message": f"{cleaned_count} arquivo(s) removido(s) com sucesso"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao limpar arquivos: {str(e)}")


@app.get("/list-groups")
async def list_groups():
    """Lista todos os grupos do Telegram"""
    try:
        telegram_client = await get_telegram_client()
        grupos = []
        
        async for dialog in telegram_client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                grupos.append({
                    "id": dialog.id,
                    "title": dialog.name,
                    "is_group": dialog.is_group,
                    "is_channel": dialog.is_channel
                })
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "groups": grupos,
                "total": len(grupos)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar grupos: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

