from flask import Flask, render_template, request, jsonify, send_file
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import threading
import queue
import os
import json
import time
from datetime import datetime
import uuid

app = Flask(__name__)

# Configurações globais
VOICES = {
    'pf_dora': 'Dora (Feminina)',
    'pm_alex': 'Alex (Masculino)', 
    'pm_santa': 'Santa (Masculino)'
}

class AudioGenerator:
    def __init__(self):
        self.pipeline = None
        self.audio_queue = queue.Queue()
        self.current_paragraph = 0
        self.is_generating = False
        self.paragraphs = []
        self.audio_files = []
        
    def init_pipeline(self):
        if not self.pipeline:
            self.pipeline = KPipeline(lang_code="p")
    
    def split_text(self, text):
        """Divide o texto em parágrafos"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [text.strip()]
        return paragraphs
    
    def generate_audio_for_paragraph(self, paragraph, voice, paragraph_index):
        """Gera áudio para um parágrafo específico"""
        try:
            self.init_pipeline()
            
            generator = self.pipeline(paragraph, voice=voice)
            audio_chunks = []
            
            for gs, ps, audio in generator:
                audio_chunks.append(audio)
            
            if audio_chunks:
                audio_data = np.concatenate(audio_chunks)
                
                # Salvar arquivo de áudio
                filename = f"audio_para_{paragraph_index}_{uuid.uuid4().hex[:8]}.wav"
                sf.write(filename, audio_data, 24000)
                
                return {
                    'paragraph_index': paragraph_index,
                    'text': paragraph,
                    'audio_file': filename,
                    'duration': len(audio_data) / 24000,  # duração em segundos
                    'status': 'completed'
                }
            else:
                return {
                    'paragraph_index': paragraph_index,
                    'text': paragraph,
                    'audio_file': None,
                    'duration': 0,
                    'status': 'error'
                }
                
        except Exception as e:
            return {
                'paragraph_index': paragraph_index,
                'text': paragraph,
                'audio_file': None,
                'duration': 0,
                'status': 'error',
                'error': str(e)
            }

# Instância global do gerador
audio_generator = AudioGenerator()

@app.route('/')
def index():
    return render_template('index.html', voices=VOICES)

@app.route('/generate', methods=['POST'])
def generate_audio():
    data = request.get_json()
    text = data.get('text', '').strip()
    voice = data.get('voice', 'pm_alex')
    
    if not text:
        return jsonify({'error': 'Texto não pode estar vazio'}), 400
    
    # Dividir texto em parágrafos
    paragraphs = audio_generator.split_text(text)
    
    # Iniciar geração em background
    def generate_all():
        audio_generator.is_generating = True
        audio_generator.paragraphs = paragraphs
        audio_generator.audio_files = []
        
        for i, paragraph in enumerate(paragraphs):
            if not audio_generator.is_generating:  # Verificar se foi cancelado
                break
                
            result = audio_generator.generate_audio_for_paragraph(paragraph, voice, i)
            audio_generator.audio_files.append(result)
            
            # Notificar progresso via WebSocket seria ideal, mas por simplicidade
            # vamos usar polling no frontend
    
    thread = threading.Thread(target=generate_all)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': 'Geração iniciada',
        'total_paragraphs': len(paragraphs),
        'paragraphs': paragraphs
    })

@app.route('/status')
def get_status():
    return jsonify({
        'is_generating': audio_generator.is_generating,
        'paragraphs': audio_generator.paragraphs,
        'audio_files': audio_generator.audio_files,
        'total_paragraphs': len(audio_generator.paragraphs),
        'completed': len([f for f in audio_generator.audio_files if f.get('status') == 'completed'])
    })

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_file(filename, mimetype='audio/wav')

@app.route('/cancel', methods=['POST'])
def cancel_generation():
    audio_generator.is_generating = False
    return jsonify({'message': 'Geração cancelada'})

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Remove arquivos de áudio temporários"""
    try:
        for audio_file in audio_generator.audio_files:
            if audio_file.get('audio_file') and os.path.exists(audio_file['audio_file']):
                os.remove(audio_file['audio_file'])
        audio_generator.audio_files = []
        return jsonify({'message': 'Arquivos limpos'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
