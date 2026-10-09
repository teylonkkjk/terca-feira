import speech_recognition as sr

def listen_command(ui):
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        # Agora ela é direta e elegante
        ui.log("Escutando...") 
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language='pt-BR')
            ui.log(f"> {text.upper()}") # Escreve o que você disse em maiúsculo (futurista)
            return text.lower()
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            ui.log("[ERRO] Sem conexão para transcrição.")
            return None