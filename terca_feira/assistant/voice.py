import sounddevice as sd
import numpy as np
from colorama import Fore, Style

def test_microphone(duration=5):
    """
    Testa o microfone capturando o volume por alguns segundos.
    Exibe uma barra gráfica no terminal para mostrar a captação.
    """
    print(f"\n{Fore.YELLOW}Iniciando teste de microfone por {duration} segundos...{Style.RESET_ALL}")
    print("Fale algo ou faça barulho (bata palmas) para testar!")
    
    def audio_callback(indata, frames, time, status):
        if status:
            print(status)
        # Calcula a força do áudio (RMS - Root Mean Square)
        volume_norm = np.linalg.norm(indata) * 10
        # Cria uma "barra" visual baseada no volume
        bar = '|' * int(volume_norm)
        # O '\r' faz com que a linha se atualize no mesmo lugar
        print(f"Volume: {bar:50}", end='\r')

    try:
        # Inicia um fluxo de escuta não-bloqueante
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100):
            sd.sleep(duration * 1000) # Mantém escutando pelo tempo definido
            
        print(f"\n\n{Fore.GREEN}Teste de microfone concluído com sucesso! A Terça Feira consegue te ouvir.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n\n{Fore.RED}Erro ao acessar o microfone: {e}{Style.RESET_ALL}")