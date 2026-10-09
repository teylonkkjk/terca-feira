import os
from pathlib import Path
from assistant.tts import speak

# Descobre automaticamente a pasta raiz do usuário atual (ex: C:\Users\teylon)
USER_HOME = Path.home()

# Mapeia as pastas mais comuns do Windows
PASTAS_COMUNS = {
    "downloads": USER_HOME / "Downloads",
    "documentos": USER_HOME / "Documents",
    "área de trabalho": USER_HOME / "Desktop",
    "desktop": USER_HOME / "Desktop",
    "imagens": USER_HOME / "Pictures",
    "músicas": USER_HOME / "Music",
    "vídeos": USER_HOME / "Videos"
}

def manage_folders(comando, ui):
    """
    Interpreta comandos para criar ou abrir pastas.
    Retorna True se executou alguma ação.
    """
    # 1. CRIAR UMA PASTA NA ÁREA DE TRABALHO
    if "criar pasta" in comando or "crie uma pasta" in comando or "criar uma pasta" in comando:
        # Lógica simples para pegar o nome da pasta
        # Se você disser "crie uma pasta chamada projetos", ele pega a palavra "projetos"
        nome_pasta = "Nova_Pasta_Assistente" # Nome padrão
        
        if "chamada" in comando:
            # Corta a frase no meio, pegando tudo o que vem depois de "chamada"
            partes = comando.split("chamada")
            if len(partes) > 1:
                # Remove espaços vazios e deixa a primeira letra maiúscula
                nome_pasta = partes[1].strip().title()
                
        caminho_nova_pasta = PASTAS_COMUNS["desktop"] / nome_pasta
        
        try:
            # exist_ok=True impede que o programa quebre se a pasta já existir
            os.makedirs(caminho_nova_pasta, exist_ok=True)
            speak(f"Feito. A pasta {nome_pasta} foi criada na sua área de trabalho.", ui)
            return True
        except Exception as e:
            speak("Houve um erro de permissão ao tentar criar a pasta.", ui)
            ui.log(f"[ERRO] {e}")
            return True

    # 2. ABRIR UMA PASTA EXISTENTE
    if "abrir pasta" in comando or "abra a pasta" in comando or "minha pasta" in comando:
        for nome, caminho in PASTAS_COMUNS.items():
            if nome in comando:
                if caminho.exists():
                    speak(f"Abrindo sua pasta de {nome}.", ui)
                    # O startfile simula um "duplo clique" do mouse no Windows
                    os.startfile(caminho)
                else:
                    speak(f"Não consegui encontrar a pasta {nome}.", ui)
                return True
                
        speak("Não tenho certeza de qual pasta você quer abrir.", ui)
        return True

    return False