"""
application.py - Inicializador de Aplicativos Windows.
"""

import os
import re
import subprocess
import logging
from assistant.tts import speak

logger = logging.getLogger("TercaFeira.AppLauncher")

class AppLauncher:
    APPS_RAPIDOS = {
        "navegador": "chrome", "chrome": "chrome", "google": "chrome",
        "edge": "msedge", "bloco de notas": "notepad", "vs code": "code",
        "visual studio": "code", "spotify": "spotify", "calculadora": "calc",
        "discord": "discord", "explorador de arquivos": "explorer",
        "pastas": "explorer", "cmd": "cmd"
    }

    def __init__(self):
        self._cache_atalhos = {}
        self._cache_construido = False

    def _construir_cache(self):
        if self._cache_construido: return
        caminhos = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")
        ]
        for base in caminhos:
            if not os.path.exists(base): continue
            for r, _, arqs in os.walk(base):
                for a in arqs:
                    if a.endswith(".lnk"):
                        self._cache_atalhos[a.lower().replace(".lnk", "")] = os.path.join(r, a)
        self._cache_construido = True

    def abrir_aplicativo(self, comando: str, ui) -> bool:
        cmd = comando.lower()

        # 1. Dicionário
        for k, v in self.APPS_RAPIDOS.items():
            if re.search(rf'\b{k}\b', cmd):
                speak(f"Abrindo o {k}.", ui)
                subprocess.Popen(f"start {v}", shell=True)
                return True

        # 2. Busca Dinâmica Segura
        match = re.search(r'(abra|abrir|iniciar|executar)\s*(o |a |um |uma )?(.+)', cmd)
        if match:
            app_cru = match.group(3).strip().replace(".", "").replace("?", "")
            nome_app = re.sub(r'[&|;<>^]', '', app_cru).strip() # Sanitização
            if not nome_app: return False

            ui.log(f"[SISTEMA] Procurando: '{nome_app}'...")
            self._construir_cache()

            for atalho, path in self._cache_atalhos.items():
                if nome_app in atalho:
                    speak(f"Iniciando {nome_app}.", ui)
                    os.startfile(path)
                    return True

            ui.log(f"[SISTEMA] Tentando bypass no PATH...")
            res = subprocess.run(f"start {nome_app}", shell=True, capture_output=True)
            if res.returncode == 0:
                speak("Comando enviado.", ui)
            else:
                speak(f"Não encontrei {nome_app}.", ui)
            return True
            
        return False

_launcher = AppLauncher()
def open_application(comando: str, ui) -> bool:
    return _launcher.abrir_aplicativo(comando, ui)