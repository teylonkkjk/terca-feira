import os
import time
import pygame
import asyncio
import edge_tts
import pyttsx3

# ==========================================
# PLANO B: Voz offline robótica de segurança
# ==========================================
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if "Brazil" in voice.name or "PT-BR" in voice.name.upper():
        engine.setProperty('voice', voice.id)
        break
engine.setProperty('rate', 190)

pygame.mixer.init()

# ==========================================
# PLANO A: Voz Neural Premium (Azure/Edge)
# ==========================================
async def generate_premium_audio(text, filename):
    """
    Usa a voz Neural da Francisca e acelera em +20% para respostas rápidas.
    """
    voz = "pt-BR-FranciscaNeural"
    velocidade = "+20%" 
    
    communicate = edge_tts.Communicate(text, voz, rate=velocidade)
    await communicate.save(filename)

def speak(text, ui=None):
    if ui:
        ui.log(f"Terça Feira: {text}")
        
    try:
        filename = "voz_temporaria.mp3"
        
        # CORREÇÃO: Criando um loop assíncrono seguro para Threads no Windows
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_premium_audio(text, filename))
        loop.close()
        
        # Toca o áudio instantaneamente
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.05) 
            
        pygame.mixer.music.unload()
        try:
            os.remove(filename)
        except:
            pass
            
    except Exception as e:
        # Agora o erro real vai aparecer no painel para sabermos o que houve!
        if ui:
            ui.log(f"[AVISO] Falha na voz neural: {e}")
        engine.say(text)
        engine.runAndWait()