import sys
import os
import time
import threading
from colorama import init, Fore, Style

from config import ASSISTANT_NAME, USER_NAME
from interface.terminal_ui import TerminalUI

# --- IMPORTS DO ECOSSISTEMA NEURAL ---
from computer.audio import ouvir_whisper
from assistant.tts import speak
from assistant.brain import process_command_autonomo

init(autoreset=True)

def loop_de_consciencia(ui):
    """
    Thread Trabalhadora. Roda em modo fantasma.
    """
    time.sleep(1.5)
    print(f"\n{Fore.CYAN}=== {ASSISTANT_NAME} ONLINE EM MODO FANTASMA ==={Style.RESET_ALL}")
    
    # Removemos o ui.show() daqui. A interface nasce 100% invisível.
    ui.clear()
    ui.log(f"--- SISTEMA {ASSISTANT_NAME} INICIADO ---")
    ui.log("[STANDBY] Sistema invisível e aguardando palavra de despertar...")
    
    while True:
        comando = ouvir_whisper(ui)
        if comando:
            process_command_autonomo(comando, ui)
        time.sleep(0.1)

def main():
    # 1. Inicializa o Motor Gráfico (HUD)
    ui = TerminalUI(ASSISTANT_NAME)
    
    # 2. Inicia a "Consciência" da IA numa Thread isolada (Multithreading Real)
    # A flag daemon=True garante que, se fechar a janela, a IA morre junto automaticamente.
    brain_thread = threading.Thread(target=loop_de_consciencia, args=(ui,), daemon=True)
    brain_thread.start()
    
    try:
        # 3. Bloqueia a Main Thread EXCLUSIVAMENTE com o Loop do Tkinter.
        # Isso garante a fluidez perfeita da animação geométrica e do visualizador de áudio.
        ui.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Sistema encerrado forçadamente pelo usuário.{Style.RESET_ALL}")
        os._exit(0)

if __name__ == "__main__":
    main()