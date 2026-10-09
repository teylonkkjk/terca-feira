"""
music.py - Módulo de Mídia (YouTube Player).
Forçado para reprodução através do navegador Brave.
"""

import urllib.request
import urllib.parse
import re
import os
import subprocess
import logging
from assistant.tts import speak

logger = logging.getLogger("TercaFeira.Media")

class MediaManager:
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0'}

    def processar_comando(self, comando: str, ui) -> bool:
        cmd = comando.lower()
        musica = ""
        
        for g in ["toca a música ", "tocar a música ", "toca ", "tocar ", "toque ", "põe a música "]:
            if g in cmd:
                musica = cmd.split(g)[1].strip()
                break
                
        if not musica: return False

        speak(f"Buscando {musica} no YouTube...", ui)
        try:
            req = urllib.request.Request(f"https://www.youtube.com/results?search_query={urllib.parse.quote(musica)}", headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=5.0) as res:
                html = res.read().decode('utf-8')
            ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
            
            if ids:
                url = f"https://www.youtube.com/watch?v={ids[0]}"
                ui.log(f"[MÍDIA] Reproduzindo: {url}")
                
                # Caminhos padrão onde o Windows instala o Brave
                brave_paths = [
                    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe")
                ]
                
                brave_encontrado = False
                for path in brave_paths:
                    if os.path.exists(path):
                        ui.log("[MÍDIA] Iniciando via Brave Browser.")
                        # Popen abre o processo de forma isolada (não trava a IA)
                        subprocess.Popen([path, url])
                        brave_encontrado = True
                        break
                        
                # Fallback: Se o utilizador não tiver o Brave instalado, usa o navegador padrão
                if not brave_encontrado:
                    ui.log("[AVISO] Brave não encontrado. Iniciando no navegador padrão.")
                    subprocess.run(f'start "" "{url}"', shell=True, capture_output=True)
            else:
                speak("Não encontrei o vídeo.", ui)
        except Exception as e:
            logger.error(f"Erro ao acessar YouTube: {e}")
            speak("Sem conexão com servidores de mídia.", ui)
            
        return True

_media = MediaManager()
def play_music(comando: str, ui) -> bool:
    return _media.processar_comando(comando, ui)