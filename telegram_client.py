"""
Cliente Telegram para baixar vídeos de grupos automaticamente
"""
import os
import json
import asyncio
from datetime import datetime
from telethon.sync import TelegramClient, events

# Configurações do Telegram (lê de variáveis de ambiente ou usa padrões)
API_ID = int(os.getenv("TELEGRAM_API_ID", "29090427"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "88bf96af8dc0652c6f5026417b7d8f25")
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "telegram_session")

# Importar Whisper para transcrição (opcional - só importa se disponível)
try:
    import whisper
    WHISPER_DISPONIVEL = True
except ImportError:
    WHISPER_DISPONIVEL = False


# Inicializar o cliente
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Pasta para salvar vídeos
DOWNLOADS_FOLDER = "videos_baixados"
os.makedirs(DOWNLOADS_FOLDER, exist_ok=True)

# Arquivo para controlar vídeos já baixados (pode ser sobrescrito pela API)
CONTROLE_BAIXADOS = os.getenv("CONTROLE_BAIXADOS", "videos_baixados.json")


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
    
    # Criar ID único: chat_id + message_id + file_id (se disponível)
    # Obter chat_id de diferentes formas dependendo do contexto
    chat_id = None
    if hasattr(message, 'chat_id'):
        chat_id = message.chat_id
    elif hasattr(message, 'peer_id'):
        chat_id = message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else message.peer_id
    
    message_id = message.id
    file_id = None
    
    # Tentar obter file_id do vídeo (ID único do arquivo no Telegram)
    if message.video:
        file_id = message.video.id if hasattr(message.video, 'id') else None
    elif message.media and hasattr(message.media, 'document'):
        if hasattr(message.media.document, 'id'):
            file_id = message.media.document.id
        elif hasattr(message.media.document, 'file_reference'):
            file_id = str(message.media.document.file_reference) if message.media.document.file_reference else None
    
    # Criar ID único combinando essas informações
    # Formato: chat_id_message_id_file_id ou chat_id_message_id
    if file_id:
        video_id = f"{chat_id}_{message_id}_{file_id}"
    else:
        video_id = f"{chat_id}_{message_id}"
    
    return video_id in videos_baixados, video_id


async def listar_grupos():
    """Lista todos os grupos/chats do usuário"""
    grupos = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            grupos.append({
                'id': dialog.id,
                'title': dialog.name,
                'entity': dialog.entity
            })
    return grupos


async def selecionar_grupo():
    """Permite ao usuário selecionar um grupo"""
    print("\n📋 Buscando seus grupos...\n")
    grupos = await listar_grupos()
    
    if not grupos:
        print("❌ Nenhum grupo encontrado!")
        return None
    
    print("Grupos encontrados:\n")
    for i, grupo in enumerate(grupos, 1):
        print(f"{i}. {grupo['title']} (ID: {grupo['id']})")
    
    while True:
        try:
            escolha = input(f"\n👉 Escolha o número do grupo (1-{len(grupos)}): ")
            indice = int(escolha) - 1
            if 0 <= indice < len(grupos):
                grupo_selecionado = grupos[indice]
                print(f"\n✅ Grupo selecionado: {grupo_selecionado['title']}\n")
                return grupo_selecionado['entity']
            else:
                print("❌ Número inválido!")
        except ValueError:
            print("❌ Por favor, digite um número válido!")
        except KeyboardInterrupt:
            print("\n\n❌ Operação cancelada.")
            return None


async def baixar_video(message, grupo_nome, usar_data_mensagem=False, transcrever=False):
    """Baixa um vídeo de uma mensagem"""
    try:
        # Verificar se já foi baixado
        ja_baixado, video_id = verificar_se_ja_baixado(message)
        if ja_baixado:
            print(f"⏭️ Vídeo já baixado anteriormente (ID: {video_id}) - Pulando...")
            return None
        
        # Criar pasta com nome do grupo se não existir
        pasta_grupo = os.path.join(DOWNLOADS_FOLDER, grupo_nome.replace('/', '_').replace('\\', '_'))
        os.makedirs(pasta_grupo, exist_ok=True)
        
        # Usar data da mensagem ou data de hoje
        if usar_data_mensagem and message.date:
            data_msg = message.date.strftime("%Y-%m-%d")
            pasta_data = os.path.join(pasta_grupo, data_msg)
        else:
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            pasta_data = os.path.join(pasta_grupo, data_hoje)
        
        os.makedirs(pasta_data, exist_ok=True)
        
        # Baixar o vídeo
        nome_arquivo = await client.download_media(
            message, 
            file=pasta_data
        )
        
        if nome_arquivo:
            # Salvar ID do vídeo baixado
            salvar_video_baixado(video_id)
            
            tamanho = os.path.getsize(nome_arquivo) / (1024 * 1024)  # MB
            print(f"✅ Vídeo baixado: {os.path.basename(nome_arquivo)} ({tamanho:.2f} MB)")
            
            # Transcrever se solicitado
            if transcrever and WHISPER_DISPONIVEL:
                transcrever_video(nome_arquivo)
            
            return nome_arquivo
        else:
            print("⚠️ Erro ao baixar vídeo")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao baixar vídeo: {str(e)}")
        return None


def verificar_ffmpeg():
    """Verifica se o FFmpeg está instalado"""
    import subprocess
    import glob
    
    # Tentar executar direto (se estiver no PATH)
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    # Tentar encontrar em locais comuns do Windows
    caminhos_comuns = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", "*FFmpeg*", "**", "ffmpeg.exe"),
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "ffmpeg", "bin", "ffmpeg.exe"),
    ]
    
    for padrao in caminhos_comuns:
        try:
            matches = glob.glob(padrao, recursive=True)
            if matches and os.path.exists(matches[0]):
                # Testar se funciona
                try:
                    subprocess.run([matches[0], "-version"], capture_output=True, check=True, timeout=5)
                    # Adicionar ao PATH temporariamente para esta sessão
                    os.environ["PATH"] = os.path.dirname(matches[0]) + os.pathsep + os.environ.get("PATH", "")
                    return True
                except:
                    continue
        except:
            continue
    
    return False


def transcrever_video(caminho_video):
    """Transcreve um vídeo usando Whisper"""
    if not WHISPER_DISPONIVEL:
        print("⚠️ Whisper não está instalado. Execute: pip install openai-whisper")
        return None
    
    # Verificar se FFmpeg está disponível
    if not verificar_ffmpeg():
        print("❌ FFmpeg não encontrado!")
        print("   O Whisper precisa do FFmpeg para processar vídeos.")
        print("\n   Para instalar o FFmpeg no Windows:")
        print("   1. Baixe em: https://www.gyan.dev/ffmpeg/builds/")
        print("   2. Extraia o arquivo")
        print("   3. Adicione a pasta 'bin' ao PATH do sistema")
        print("   4. Ou instale via Chocolatey: choco install ffmpeg")
        print("   5. Ou via winget: winget install ffmpeg")
        return None
    
    try:
        print(f"🎤 Transcrevendo vídeo: {os.path.basename(caminho_video)}...")
        
        # Verificar se o arquivo existe
        if not os.path.exists(caminho_video):
            print(f"❌ Arquivo não encontrado: {caminho_video}")
            return None
        
        # Carregar modelo Whisper (base é um bom equilíbrio entre velocidade e qualidade)
        # Outras opções: tiny, small, medium, large
        model = whisper.load_model("base")
        
        # Transcrever o vídeo
        resultado = model.transcribe(caminho_video, language="pt")
        
        # Extrair texto transcrito
        texto_transcrito = resultado["text"].strip()
        
        # Salvar transcrição em arquivo .txt
        caminho_txt = os.path.splitext(caminho_video)[0] + "_transcricao.txt"
        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(texto_transcrito)
        
        print(f"✅ Transcrição salva: {os.path.basename(caminho_txt)}")
        
        # Mostrar preview da transcrição (primeiros 150 caracteres)
        preview = texto_transcrito[:150] + "..." if len(texto_transcrito) > 150 else texto_transcrito
        print(f"📝 Preview: {preview}\n")
        
        return texto_transcrito, caminho_txt
        
    except FileNotFoundError as e:
        if "ffmpeg" in str(e).lower():
            print("❌ FFmpeg não encontrado! Verifique se está instalado e no PATH.")
            print("   Instale o FFmpeg: https://www.gyan.dev/ffmpeg/builds/")
        else:
            print(f"❌ Arquivo não encontrado: {str(e)}")
        return None, None
    except Exception as e:
        print(f"❌ Erro ao transcrever vídeo: {str(e)}")
        print("   💡 Dica: Verifique se o FFmpeg está instalado corretamente")
        return None, None


async def baixar_videos_existentes(grupo_entity, limite=None, transcrever=False):
    """Baixa vídeos já existentes no grupo"""
    grupo_nome = grupo_entity.title if hasattr(grupo_entity, 'title') else str(grupo_entity.id)
    
    print(f"\n🔍 Procurando vídeos no grupo: {grupo_nome}")
    print("⏳ Isso pode levar um tempo dependendo da quantidade de mensagens...\n")
    
    videos_encontrados = 0
    videos_baixados = 0
    videos_pulados = 0
    videos_erro = 0
    
    try:
        # Buscar mensagens do grupo
        async for message in client.iter_messages(grupo_entity, limit=limite):
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
                data_msg = message.date.strftime("%Y-%m-%d %H:%M:%S") if message.date else "data_desconhecida"
                
                # Verificar se já foi baixado antes de tentar
                ja_baixado, video_id = verificar_se_ja_baixado(message)
                if ja_baixado:
                    videos_pulados += 1
                    print(f"\n⏭️ Vídeo {videos_encontrados} já baixado (pulando) - {data_msg}")
                else:
                    print(f"\n📹 Vídeo {videos_encontrados} encontrado (de {data_msg})")
                
                    # Baixar usando a data da mensagem
                    resultado = await baixar_video(message, grupo_nome, usar_data_mensagem=True, transcrever=transcrever)
                    
                    if resultado:
                        videos_baixados += 1
                    else:
                        # Verificar se foi pulado ou erro
                        ja_baixado_novo, _ = verificar_se_ja_baixado(message)
                        if not ja_baixado_novo:
                            videos_erro += 1
                
                # Pequeno delay para não sobrecarregar
                await asyncio.sleep(0.5)
        
        # Preparar nome do grupo para o caminho
        grupo_nome_limpo = grupo_nome.replace('/', '_').replace('\\', '_')
        caminho_salvos = os.path.join(DOWNLOADS_FOLDER, grupo_nome_limpo)
        
        print(f"\n\n📊 Resumo:")
        print(f"   📹 Vídeos encontrados: {videos_encontrados}")
        print(f"   ✅ Vídeos baixados: {videos_baixados}")
        print(f"   ⏭️ Vídeos já baixados (pulados): {videos_pulados}")
        print(f"   ❌ Erros: {videos_erro}")
        print(f"\n💾 Vídeos salvos em: {caminho_salvos}")
        
    except Exception as e:
        print(f"\n❌ Erro ao buscar vídeos: {str(e)}")
        print(f"✅ Vídeos baixados até agora: {videos_baixados}/{videos_encontrados}")


async def monitorar_grupo(grupo_entity, transcrever=False):
    """Monitora um grupo e baixa vídeos automaticamente"""
    grupo_nome = grupo_entity.title if hasattr(grupo_entity, 'title') else str(grupo_entity.id)
    
    print(f"🎬 Monitorando grupo: {grupo_nome}")
    if transcrever:
        print("🎤 Transcrição ativada - vídeos serão transcritos automaticamente")
    print("📥 Aguardando novos vídeos... (Pressione Ctrl+C para parar)\n")
    
    @client.on(events.NewMessage(chats=grupo_entity))
    async def handler(event):
        """Handler para novas mensagens no grupo"""
        message = event.message
        
        # Verificar se a mensagem tem vídeo
        if message.video:
            print(f"\n📹 Novo vídeo detectado!")
            print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Baixar o vídeo
            await baixar_video(message, grupo_nome, transcrever=transcrever)
            print()
        elif message.media and hasattr(message.media, 'document'):
            # Verificar se é um documento de vídeo
            doc = message.media.document
            if doc and hasattr(doc, 'mime_type') and doc.mime_type and 'video' in doc.mime_type:
                print(f"\n📹 Novo vídeo detectado (documento)!")
                print(f"📅 Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Baixar o vídeo
                await baixar_video(message, grupo_nome, transcrever=transcrever)
                print()
    
    # Manter o cliente rodando
    await client.run_until_disconnected()


async def main():
    """Função principal"""
    # Conectar ao Telegram
    await client.start()
    
    print("✅ Conectado ao Telegram!")
    me = await client.get_me()
    print(f"👤 Você: {me.first_name} (@{me.username if me.username else 'sem username'})")
    
    # Selecionar grupo
    grupo = await selecionar_grupo()
    
    if grupo:
        # Perguntar sobre transcrição
        transcrever = False
        if WHISPER_DISPONIVEL:
            print("\n🎤 Transcrição de vídeos")
            
            # Verificar FFmpeg antes de perguntar
            if not verificar_ffmpeg():
                print("⚠️ FFmpeg não encontrado!")
                print("   A transcrição requer FFmpeg instalado.")
                print("\n   Para instalar no Windows:")
                print("   • Opção 1 (Recomendado): winget install ffmpeg")
                print("   • Opção 2: Baixe de https://www.gyan.dev/ffmpeg/builds/")
                print("\n   Após instalar, reinicie o script.")
                print("ℹ️ Continuando sem transcrição...\n")
            else:
                transcrever_input = input("Deseja transcrever os vídeos automaticamente? (s/n): ").lower()
                transcrever = transcrever_input in ['s', 'sim', 'y', 'yes']
                if transcrever:
                    print("✅ Transcrição ativada - os vídeos serão transcritos após o download")
                else:
                    print("ℹ️ Transcrição desativada")
        else:
            print("\n⚠️ Whisper não está instalado. Para usar transcrição, execute:")
            print("   pip install openai-whisper")
            print("ℹ️ Continuando sem transcrição...\n")
        
        # Perguntar o que fazer
        print("\n📋 O que você deseja fazer?")
        print("1. 📥 Baixar vídeos já existentes no grupo")
        print("2. 👀 Monitorar e baixar novos vídeos automaticamente")
        print("3. 🔄 Fazer ambos (baixar existentes E monitorar novos)")
        
        while True:
            try:
                escolha = input("\n👉 Escolha uma opção (1-3): ")
                
                if escolha == "1":
                    # Baixar vídeos existentes
                    print("\n💡 Dica: Você pode limitar a quantidade de mensagens para processar mais rápido.")
                    limite_input = input("Quantas mensagens verificar? (Enter para todas): ")
                    limite = int(limite_input) if limite_input.strip() else None
                    
                    await baixar_videos_existentes(grupo, limite, transcrever=transcrever)
                    print("\n✅ Download concluído!")
                    break
                    
                elif escolha == "2":
                    # Monitorar novos vídeos
                    try:
                        await monitorar_grupo(grupo, transcrever=transcrever)
                    except KeyboardInterrupt:
                        print("\n\n⏹️ Monitoramento interrompido.")
                    break
                    
                elif escolha == "3":
                    # Fazer ambos
                    print("\n💡 Dica: Você pode limitar a quantidade de mensagens para processar mais rápido.")
                    limite_input = input("Quantas mensagens verificar? (Enter para todas): ")
                    limite = int(limite_input) if limite_input.strip() else None
                    
                    await baixar_videos_existentes(grupo, limite, transcrever=transcrever)
                    
                    print("\n\n🔄 Agora iniciando monitoramento de novos vídeos...")
                    print("📥 Pressione Ctrl+C para parar o monitoramento.\n")
                    
                    try:
                        await monitorar_grupo(grupo, transcrever=transcrever)
                    except KeyboardInterrupt:
                        print("\n\n⏹️ Monitoramento interrompido.")
                    break
                else:
                    print("❌ Opção inválida! Escolha 1, 2 ou 3.")
                    
            except ValueError:
                print("❌ Por favor, digite um número válido!")
            except KeyboardInterrupt:
                print("\n\n❌ Operação cancelada.")
                break
    else:
        print("❌ Nenhum grupo selecionado. Saindo...")


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
