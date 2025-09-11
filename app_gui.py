import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from kokoro import KPipeline
import soundfile as sf
import numpy as np
import threading
import os
from datetime import datetime

class TextToSpeechGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech - Kokoro")
        self.root.geometry("800x600")
        
        # Variáveis
        self.pipeline = None
        self.is_processing = False
        
        # Configurar interface
        self.setup_ui()
        
        # Inicializar pipeline em thread separada
        self.init_pipeline()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Text to Speech com Kokoro", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Label para texto
        ttk.Label(main_frame, text="Digite o texto para converter em áudio:").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Área de texto
        self.text_area = scrolledtext.ScrolledText(main_frame, height=15, width=80)
        self.text_area.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Frame para controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configurações de voz
        ttk.Label(controls_frame, text="Voz:").grid(row=0, column=0, padx=(0, 5))
        self.voice_var = tk.StringVar(value="pm_alex")
        voice_combo = ttk.Combobox(controls_frame, textvariable=self.voice_var, 
                                  values=["pm_alex", "pm_maria", "pm_joao"], width=15)
        voice_combo.grid(row=0, column=1, padx=(0, 20))
        
        # Botão de geração
        self.generate_btn = ttk.Button(controls_frame, text="Gerar Áudio", 
                                      command=self.generate_audio)
        self.generate_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Botão de reproduzir
        self.play_btn = ttk.Button(controls_frame, text="Reproduzir", 
                                  command=self.play_audio, state="disabled")
        self.play_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Botão de salvar
        self.save_btn = ttk.Button(controls_frame, text="Salvar Como...", 
                                  command=self.save_audio, state="disabled")
        self.save_btn.grid(row=0, column=4)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Status
        self.status_var = tk.StringVar(value="Pronto para gerar áudio")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        # Texto de exemplo
        example_text = '''Digite aqui o texto que você deseja converter em áudio.

Por exemplo:
"Olá! Este é um exemplo de texto que será convertido em áudio usando a biblioteca Kokoro. A tecnologia de text-to-speech permite que computadores leiam texto em voz alta de forma natural e fluida."

Você pode inserir qualquer texto em português e clicar em "Gerar Áudio" para criar um arquivo de áudio.'''
        
        self.text_area.insert(tk.END, example_text)
    
    def init_pipeline(self):
        """Inicializa o pipeline em thread separada"""
        def init():
            try:
                self.status_var.set("Inicializando pipeline...")
                self.pipeline = KPipeline(lang_code="p")
                self.status_var.set("Pipeline inicializado! Pronto para gerar áudio")
            except Exception as e:
                self.status_var.set(f"Erro ao inicializar: {str(e)}")
                messagebox.showerror("Erro", f"Erro ao inicializar pipeline: {str(e)}")
        
        thread = threading.Thread(target=init)
        thread.daemon = True
        thread.start()
    
    def generate_audio(self):
        """Gera o áudio do texto inserido"""
        if self.is_processing:
            return
        
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Aviso", "Por favor, digite algum texto!")
            return
        
        if not self.pipeline:
            messagebox.showerror("Erro", "Pipeline ainda não foi inicializado. Aguarde um momento.")
            return
        
        self.is_processing = True
        self.generate_btn.config(state="disabled")
        self.progress.start()
        self.status_var.set("Gerando áudio...")
        
        def generate():
            try:
                # Gerar áudio
                generator = self.pipeline(text, voice=self.voice_var.get())
                audio_chunks = []
                
                for gs, ps, audio in generator:
                    audio_chunks.append(audio)
                
                if audio_chunks:
                    self.audio_data = np.concatenate(audio_chunks)
                    self.sample_rate = 24000
                    
                    # Salvar arquivo temporário
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    self.temp_filename = f"audio_{timestamp}.wav"
                    sf.write(self.temp_filename, self.audio_data, self.sample_rate)
                    
                    # Atualizar interface
                    self.root.after(0, self.generation_complete)
                else:
                    self.root.after(0, lambda: self.generation_error("Nenhum áudio foi gerado"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.generation_error(str(e)))
        
        thread = threading.Thread(target=generate)
        thread.daemon = True
        thread.start()
    
    def generation_complete(self):
        """Chamado quando a geração de áudio é concluída"""
        self.is_processing = False
        self.generate_btn.config(state="normal")
        self.play_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.progress.stop()
        self.status_var.set(f"Áudio gerado com sucesso! Arquivo: {self.temp_filename}")
        messagebox.showinfo("Sucesso", "Áudio gerado com sucesso!")
    
    def generation_error(self, error_msg):
        """Chamado quando há erro na geração"""
        self.is_processing = False
        self.generate_btn.config(state="normal")
        self.progress.stop()
        self.status_var.set(f"Erro: {error_msg}")
        messagebox.showerror("Erro", f"Erro ao gerar áudio: {error_msg}")
    
    def play_audio(self):
        """Reproduz o áudio gerado"""
        if hasattr(self, 'temp_filename') and os.path.exists(self.temp_filename):
            try:
                os.startfile(self.temp_filename)  # Windows
            except:
                messagebox.showinfo("Reproduzir", f"Arquivo salvo como: {self.temp_filename}")
        else:
            messagebox.showwarning("Aviso", "Nenhum áudio disponível para reproduzir")
    
    def save_audio(self):
        """Salva o áudio com nome personalizado"""
        if hasattr(self, 'audio_data'):
            filename = filedialog.asksaveasfilename(
                defaultextension=".wav",
                filetypes=[("Arquivos WAV", "*.wav"), ("Todos os arquivos", "*.*")],
                title="Salvar áudio como..."
            )
            if filename:
                try:
                    sf.write(filename, self.audio_data, self.sample_rate)
                    messagebox.showinfo("Sucesso", f"Áudio salvo como: {filename}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        else:
            messagebox.showwarning("Aviso", "Nenhum áudio disponível para salvar")

def main():
    root = tk.Tk()
    app = TextToSpeechGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

