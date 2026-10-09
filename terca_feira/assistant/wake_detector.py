import sounddevice as sd
import numpy as np
import time
import speech_recognition as sr
from colorama import Fore, Style

CLAP_THRESHOLD = 40  
COOLDOWN = 1.0       

def wait_for_clap():
    recognizer = sr.Recognizer()
    
    while True:
        print(f"\n{Fore.MAGENTA}Aguardando som de ativação (palma)...{Style.RESET_ALL}")
        clap_detected = False

        def audio_callback(indata, frames, time_info, status):
            nonlocal clap_detected
            volume_pico = np.max(np.abs(indata)) * 100
            if volume_pico > CLAP_THRESHOLD:
                clap_detected = True

        # PASSO 1: Ouve o ambiente até detectar a palma
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100, blocksize=1024):
            while not clap_detected:
                sd.sleep(100) 
                
        print(f"{Fore.YELLOW}Palma detectada! Aguardando você dizer o nome dela...{Style.RESET_ALL}")
        
        # PASSO 2: A palma liberou o microfone, agora espera você falar o nome em até 3 segundos
        with sr.Microphone() as source:
            try:
                # Escuta rapidinho por no máximo 3 segundos
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                text = recognizer.recognize_google(audio, language='pt-BR').lower()
                
                if "terça" in text or "feira" in text or "desperta" in text:
                    print(f"{Fore.GREEN}Nome confirmado! Acordando o sistema...{Style.RESET_ALL}")
                    return True # Acorda a assistente de verdade
                else:
                    print(f"{Fore.RED}Nome não reconhecido ({text}). Abortando.{Style.RESET_ALL}")
                    
            except sr.WaitTimeoutError:
                print(f"{Fore.RED}Você não disse o nome a tempo. Abortando.{Style.RESET_ALL}")
            except Exception:
                pass
        
        # Se falhou, volta silenciosamente para o Passo 1
        time.sleep(COOLDOWN)