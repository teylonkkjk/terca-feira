"""
audio.py - Módulo de Reconhecimento de Voz (STT).
Implementação in-memory com Máquina de Estados e Controle Visual (Holograma).
"""

import whisper
import sounddevice as sd
import numpy as np
import logging
import warnings
from assistant.tts import speak

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] AUDIO: %(message)s")
logger = logging.getLogger(__name__)

class VoiceEngine:
    ALUCINACOES_COMUNS = ["obrigado por assistir", "obrigada por assistir", "legendas pela comunidade", "obrigado.", "amém", "inscreva-se"]

    def __init__(self):
        self._modelo = None
        self.acordada = False  

    def inicializar(self, ui) -> None:
        if self._modelo is None:
            ui.log("[SISTEMA] Carregando motor neural Whisper SMALL...")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._modelo = whisper.load_model("small")

    def escutar(self, ui, duracao_padrao: float = 5.0) -> str:
        self.inicializar(ui)
        if not self._modelo: return ""

        duracao = duracao_padrao if self.acordada else 3.0

        if self.acordada:
            ui.log(f"[OUVINDO] Aguardando comando... ({duracao}s)")
        else:
            ui.log(f"[STANDBY] Aguardando chamada ('Terça Feira')... ({duracao}s)")

        try:
            audio_data = sd.rec(int(duracao * 16000), samplerate=16000, channels=1, dtype=np.float32)
            sd.wait()
            audio_array = audio_data.flatten()
        except Exception as e:
            logger.error(f"Erro de microfone: {e}")
            return ""

        if self.acordada:
            ui.log("[PROCESSANDO VOZ] Transcrevendo...")

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                res = self._modelo.transcribe(
                    audio_array, 
                    language="pt", 
                    initial_prompt="Olá. Comando de voz para a assistente Terça Feira.", 
                    fp16=False
                )
                texto = res["text"].strip()
                texto_lower = texto.lower()
                
                # Bloqueio de Ruídos e Alucinações
                if len(texto) < 4 or any('\u0400' <= c <= '\u04FF' for c in texto) or (any(f in texto_lower for f in self.ALUCINACOES_COMUNS) and len(texto) < 35):
                    if self.acordada:
                        ui.log("[SISTEMA] Ruído ignorado.")
                    return ""
                    
                # ========================================================
                # MÁQUINA DE ESTADOS E CONTROLE DO HOLOGRAMA
                # ========================================================
                
                # ESTADO 1: DORMINDO (STANDBY)
                if not self.acordada:
                    if "terça-feira" in texto_lower or "terça feira" in texto_lower or "terça" in texto_lower:
                        self.acordada = True
                        
                        ui.show() # <---- MÁGICA: FAZ A INTERFACE APARECER NA TELA
                        ui.log("[SISTEMA] >>> ASSISTENTE ATIVADA <<<")
                        
                        comando_real = texto_lower.replace("terça-feira", "").replace("terça feira", "").strip()
                        
                        if any(g in comando_real for g in ["suspender", "descansar"]):
                            self.acordada = False
                            speak("Voltando a dormir.", ui)
                            ui.hide() # <---- MÁGICA: ESCONDE A INTERFACE NOVAMENTE
                            return ""
                            
                        if len(comando_real) > 3:
                            ui.log(f"\n[VOCÊ] {comando_real}\n")
                            return comando_real
                        else:
                            speak("Sim, chefe. Pode falar.", ui)
                            return ""
                            
                    return ""

                # ESTADO 2: ACORDADA (ATIVA)
                else:
                    gatilhos_dormir = ["suspender", "descansar", "dormir", "ficar em espera"]
                    if any(g in texto_lower for g in gatilhos_dormir):
                        self.acordada = False
                        ui.log("[SISTEMA] >>> ASSISTENTE EM STANDBY <<<")
                        speak("Entendido. Entrando em modo de espera.", ui)
                        ui.hide() # <---- MÁGICA: ESCONDE A INTERFACE QUANDO VAI DORMIR
                        return ""

                    ui.log(f"\n[VOCÊ] {texto}\n")
                    return texto
                    
            except Exception:
                return ""

_motor = VoiceEngine()

def ouvir_whisper(ui, duracao_segundos: float = 5.0) -> str:
    return _motor.escutar(ui, duracao_segundos)