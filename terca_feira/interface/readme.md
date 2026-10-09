
# 🧠 Terça Feira - Assistente Pessoal de IA Local

**Terça Feira** é uma assistente virtual inteligente, 100% autônoma e focada em privacidade. Desenvolvida em Python, ela roda localmente utilizando o poder do LLM **Llama 3.1** via Ollama e o reconhecimento de voz **Whisper** da OpenAI.

## 🚀 Funcionalidades

- 🎙️ **Comandos de Voz Offline:** Transcrição de áudio extremamente rápida e precisa usando o Whisper.
- 🧠 **Cérebro Autônomo:** Utiliza *Function Calling* com Llama 3.1 para decidir autonomamente quando conversar e quando agir.
- 💾 **Memória de Longo Prazo:** Banco de dados vetorial (ChromaDB) para lembrar do contexto de conversas passadas.
- 🖥️ **Controle Total do Windows:**
  - Aumenta e diminui o volume do sistema.
  - Ajusta o brilho da tela.
  - Desliga o computador por comando de voz.
- 🌐 **Navegação e Entretenimento:**
  - Abre qualquer aplicativo instalado no computador (ex: Calculadora, Spotify, Bloco de Notas).
  - Pesquisa vídeos e músicas específicas no YouTube.
  - Realiza buscas no Google e abre sites diretamente pelo navegador.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.12
- **IA e LLM:** Ollama (Llama 3.1 8B)
- **Reconhecimento de Voz:** OpenAI Whisper + SoundDevice
- **Banco de Dados Vetorial:** ChromaDB
- **Dependências de Sistema:** FFmpeg (para processamento de áudio)

## ⚙️ Como Instalar e Rodar

### Pré-requisitos

1. Ter o [Python 3.10+](https://www.python.org/downloads/) instalado.
2. Ter o [Ollama](https://ollama.com/) instalado e rodando.
3. Ter o **FFmpeg** configurado nas variáveis de ambiente do Windows.

### Passos de Instalação

1. Clone este repositório:
   ```bash
   git clone [https://github.com/teylonkkjk/terca-feira.git](https://github.com/teylonkkjk/terca-feira.git)
   cd terca-feira
   ```
