"""
browser.py - Módulo de Navegação e RAG (DuckDuckGo + Wikipedia).
Resolve problemas de URL do Windows.
"""

import webbrowser
import urllib.parse
import re
import subprocess
import logging

import wikipedia
from duckduckgo_search import DDGS
from assistant.tts import speak

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] BROWSER: %(message)s")
logger = logging.getLogger(__name__)
wikipedia.set_lang("pt")

class WebNavigator:
    SITES = {"youtube": "https://www.youtube.com", "google": "https://www.google.com", "whatsapp": "https://web.whatsapp.com"}
    RESERVADAS = ["a", "o", "porta", "pasta", "arquivo", "navegador", "bloco de notas", "cmd"]

    @staticmethod
    def forcar_abertura(url: str, ui) -> None:
        try:
            if webbrowser.open(url, new=2): return
            subprocess.run(f'start "" "{url}"', shell=True, capture_output=True)
        except Exception as e:
            ui.log(f"[ERRO BROWSER] Falha ao tentar abrir URL: {e}")

    @classmethod
    def processar(cls, comando: str, ui) -> bool:
        cmd = comando.lower().strip()
        
        for g in ["pesquisar", "pesquise", "pesquisa", "buscar", "busca"]:
            if g in cmd:
                termo = cmd.split(g)[-1].replace("sobre ", "").strip()
                if "no youtube" in termo:
                    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(termo.replace('no youtube','').strip())}"
                else:
                    url = f"https://www.google.com/search?q={urllib.parse.quote(termo.replace('no google','').strip())}"
                cls.forcar_abertura(url, ui)
                return True

        match = re.search(r'(abra|abrir|acesse)\s+(o\s+)?(site\s+)?(da\s+|do\s+|de\s+)?(.+)', cmd)
        if match:
            alvo = match.group(5).strip().replace(".", "")
            if alvo in cls.RESERVADAS: return False
            for nome, url in cls.SITES.items():
                if nome in alvo:
                    speak(f"Abrindo {nome}.", ui)
                    cls.forcar_abertura(url, ui)
                    return True
            cls.forcar_abertura(f"https://duckduckgo.com/?q=!ducky+{urllib.parse.quote(alvo)}", ui)
            return True
        return False

class KnowledgeRetriever:
    @staticmethod
    def consultar_wikipedia(termo: str, ui):
        try: return True, wikipedia.summary(termo, sentences=2)
        except: return False, ""

def handle_browser(comando: str, comando_limpo: str, ui) -> bool:
    return WebNavigator.processar(comando, ui)