"""
Módulo de Visão Computacional.
Permite à assistente capturar e analisar o ecrã em tempo real.
"""
from PIL import ImageGrab
import io
import base64
import requests
import logging

logger = logging.getLogger("TercaFeira.Vision")

class VisionEngine:
    def __init__(self, ollama_url="http://localhost:11434/api/chat", model="llava"):
        self.ollama_url = ollama_url
        self.model = model # Requer modelo visual instalado no Ollama (ex: ollama run llava)

    def _capturar_ecra_base64(self) -> str:
        """Tira uma captura do ecrã principal e converte para Base64."""
        try:
            imagem = ImageGrab.grab()
            buffer = io.BytesIO()
            # Reduz a qualidade ligeiramente para o Ollama processar mais rápido
            imagem.save(buffer, format="JPEG", quality=70)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"Erro ao capturar o ecrã: {e}")
            return ""

    def analisar_ecra(self, pergunta: str, ui) -> str:
        ui.log("[VISÃO] A capturar frame do monitor...")
        imagem_b64 = self._capturar_ecra_base64()
        
        if not imagem_b64:
            return "Erro: Não foi possível aceder ao monitor."

        ui.log("[VISÃO] A analisar imagem com rede neural visual...")
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": pergunta,
                    "images": [imagem_b64]
                }
            ],
            "stream": False
        }

        try:
            resposta = requests.post(self.ollama_url, json=payload, timeout=90)
            resposta.raise_for_status()
            texto_ia = resposta.json().get("message", {}).get("content", "").strip()
            return f"Análise Visual: {texto_ia}"
        except Exception as e:
            logger.error(f"Falha no motor de visão: {e}")
            return "Erro: O motor de visão falhou ao processar a imagem."

_vision = VisionEngine()

def analisar_tela(pergunta: str, ui) -> str:
    return _vision.analisar_ecra(pergunta, ui)