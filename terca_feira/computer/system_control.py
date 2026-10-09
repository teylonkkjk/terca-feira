import os
import winshell
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import psutil
import PyPDF2
import docx
import re
from assistant.tts import speak

def controlar_hardware(comando_lower, ui):
    # 1. LIXEIRA
    if "lixeira" in comando_lower and ("limp" in comando_lower or "esvazi" in comando_lower or "apag" in comando_lower):
        try:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            speak("A lixeira foi esvaziada, chefe.", ui)
            return True
        except:
            speak("A lixeira já está vazia.", ui)
            return True

    # 2. BRILHO
    if "brilho" in comando_lower:
        numeros = re.findall(r'\d+', comando_lower)
        if numeros:
            nivel = int(numeros[0])
            try:
                sbc.set_brightness(nivel)
                speak(f"Brilho da tela ajustado para {nivel} por cento.", ui)
                return True
            except Exception as e:
                ui.log(f"[ERRO BRILHO] {e}")
                speak("Não consegui acessar o controle de brilho deste monitor.", ui)
                return True

    # 3. VOLUME 
    if "volume" in comando_lower:
        numeros = re.findall(r'\d+', comando_lower)
        if numeros:
            nivel = int(numeros[0]) / 100.0
            try:
                CoInitialize()
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                nivel = max(0.0, min(1.0, nivel))
                volume.SetMasterVolumeLevelScalar(nivel, None)
                speak(f"Volume alterado para {int(nivel*100)} por cento.", ui)
                return True
            except Exception as e:
                ui.log(f"[ERRO VOLUME] Método nativo falhou: {e}")
                ui.log("[SISTEMA] Acionando protocolo de volume secundário...")
                try:
                    import keyboard
                    import time
                    for _ in range(50):
                        keyboard.send("volume down")
                        time.sleep(0.01)
                    toques = int(nivel * 50) 
                    for _ in range(toques):
                        keyboard.send("volume up")
                        time.sleep(0.01)
                    speak(f"Volume ajustado para {int(nivel*100)} por cento.", ui)
                    return True
                except ImportError:
                    speak("Falha crítica no controle de áudio.", ui)
                    return True
    return False

def ler_arquivo(caminho, ui):
    texto = ""
    caminho = caminho.replace('"', '').replace("'", "").strip()
    try:
        if caminho.endswith(".txt"):
            with open(caminho, 'r', encoding='utf-8') as f:
                texto = f.read()
        elif caminho.endswith(".pdf"):
            with open(caminho, 'rb') as f:
                leitor = PyPDF2.PdfReader(f)
                texto = " ".join([pagina.extract_text() for pagina in leitor.pages if pagina.extract_text()])
        elif caminho.endswith(".docx"):
            doc = docx.Document(caminho)
            texto = " ".join([p.text for p in doc.paragraphs])
        return texto[:4000]
    except Exception as e:
        ui.log(f"[ERRO ARQUIVO] Não foi possível ler: {e}")
        return None

# ==========================================
# NOVA FUNÇÃO: GERENCIAMENTO DE ENERGIA DO PC
# ==========================================
def gerenciar_energia(comando_lower, ui):
    """Altera planos de energia e gerencia desligamento/suspensão do Windows"""
    
    # 1. TROCAR MODO DE DESEMPENHO (Usando os IDs universais do Windows)
    if "modo" in comando_lower or "energia" in comando_lower or "desempenho" in comando_lower:
        if "desempenho" in comando_lower or "gamer" in comando_lower or "máximo" in comando_lower or "alta" in comando_lower:
            # Ativa o Alto Desempenho
            os.system("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")
            speak("Modo de alto desempenho ativado. Todos os núcleos operando em capacidade máxima.", ui)
            return True
            
        elif "economia" in comando_lower or "econômico" in comando_lower:
            # Ativa a Economia de Energia
            os.system("powercfg /setactive a1841308-3541-4fab-bc81-f71556f20b4a")
            speak("Modo de economia ativado. Reduzindo o consumo de energia.", ui)
            return True
            
        elif "normal" in comando_lower or "equilibrado" in comando_lower or "padrão" in comando_lower:
            # Ativa o Equilibrado
            os.system("powercfg /setactive 381b4222-f694-41f0-9685-ff5bb260df2e")
            speak("Modo de energia equilibrado restaurado.", ui)
            return True

    # 2. DESLIGAR, REINICIAR OU SUSPENDER
    if "computador" in comando_lower or "pc" in comando_lower or "máquina" in comando_lower or "sistema" in comando_lower:
        if "reiniciar" in comando_lower:
            speak("Reiniciando o sistema. Volto em alguns instantes, chefe.", ui)
            os.system("shutdown /r /t 5") # O /t 5 dá 5 segundos de aviso antes de reiniciar
            return True
            
        elif "suspender" in comando_lower or "hibernar" in comando_lower or "dormir" in comando_lower:
            speak("Colocando o computador em suspensão. Boa noite.", ui)
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return True
            
        elif "desligar" in comando_lower:
            speak("Desligando o computador. Até a próxima, Teylon.", ui)
            os.system("shutdown /s /t 5") # 5 segundos de aviso antes de desligar a máquina
            return True
            
    return False