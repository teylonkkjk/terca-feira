"""
Módulo principal do Cérebro (Brain) da Terça Feira.
Implementa uma arquitetura de Agente Autônomo com suporte a ciclo completo de
Function Calling, injeção dinâmica de contexto e registro modular de ferramentas.
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

# Importações dos módulos externos (Preservadas conforme projeto original)
from assistant.tts import speak
from computer.system_control import controlar_hardware, ler_arquivo
from computer.browser import handle_browser
from computer.long_memory import salvar_lembranca, buscar_contexto
from computer.application import open_application
from computer.music import play_music
from computer.vision import analisar_tela
from computer.iot import acionar_iot, executar_codigo_ia
# Configuração Profissional de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("TercaFeira.Brain")

# ==============================================================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ==============================================================================
@dataclass
class BrainConfig:
    """Configurações globais do cérebro da assistente."""
    ollama_url: str = "http://localhost:11434/api/chat"
    model: str = "llama3.1"
    max_historico: int = 15
    temperature: float = 0.1  # Baixa temperatura = maior precisão em uso de ferramentas
    max_agent_iterations: int = 3  # Quantas vezes a IA pode chamar ferramentas em loop
    system_prompt: str = (
        "Você é a Terça Feira, uma assistente virtual inteligente, direta e altamente eficiente.\n"
        "REGRAS OBRIGATÓRIAS:\n"
        "1. USE FERRAMENTAS PARA TUDO. Não invente informações.\n"
        "2. Após usar uma ferramenta (como pesquisa ou controle), LEIA O RESULTADO e dê uma resposta final natural ao usuário.\n"
        "3. Se o usuário quiser apenas conversar ou você já tiver a informação, USE A FERRAMENTA 'responder_usuario'.\n"
        "4. Aja silenciosamente, nunca explique como o JSON ou suas ferramentas internas funcionam."
    )

# ==============================================================================
# GERENCIADOR DE MEMÓRIA (CONTEXTO)
# ==============================================================================
class MemoryManager:
    """Gerencia o histórico de conversas evitando o vazamento e estouro de tokens."""
    
    def __init__(self, config: BrainConfig):
        self.config = config
        self.history: List[Dict[str, str]] = []

    def append_message(self, role: str, content: str, tool_call_id: str = None) -> None:
        """Adiciona uma mensagem à memória curta (sliding window)."""
        msg = {"role": role, "content": content}
        if tool_call_id:
            msg["name"] = tool_call_id # Necessário dependendo da implementação da API (OpenAI/Ollama spec)
            
        self.history.append(msg)
        self._prune_history()

    def _prune_history(self) -> None:
        """Poda o histórico antigo mantendo apenas as interações mais recentes."""
        if len(self.history) > self.config.max_historico:
            # Remove as mensagens mais antigas mantendo o limite
            self.history = self.history[-self.config.max_historico:]

    def build_prompt_payload(self, current_input: str, long_term_memory: str) -> List[Dict[str, str]]:
        """
        Monta o payload de mensagens.
        O prompt do sistema e as memórias temporais NÃO são salvas no histórico,
        são injetadas apenas no momento da requisição para evitar poluição.
        """
        payload = [{"role": "system", "content": self.config.system_prompt}]
        
        if long_term_memory:
            contexto = f"CONTEXTO RELEVANTE DO PASSADO (Use se necessário):\n{long_term_memory}"
            payload.append({"role": "system", "content": contexto})
            
        # Adiciona o histórico recente
        payload.extend(self.history)
        
        # Adiciona a mensagem atual do usuário (já foi adicionada ao history no fluxo)
        return payload

# ==============================================================================
# REGISTRO E ABSTRAÇÃO DE FERRAMENTAS
# ==============================================================================
class ToolRegistry:
    """Gerencia as ferramentas disponíveis para a IA de forma dinâmica e escalável."""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, Callable] = {}

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], callback: Callable):
        """Registra uma nova ferramenta no ecossistema da assistente."""
        self.tools[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self.callbacks[name] = callback
        logger.debug(f"Ferramenta registrada: {name}")

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Retorna a lista formatada para a API do Ollama."""
        return list(self.tools.values())

    def execute_tool(self, name: str, arguments: Dict[str, Any], ui) -> str:
        """Executa a função mapeada para a ferramenta solicitada com tratamento de erro."""
        if name not in self.callbacks:
            msg = f"Erro: A ferramenta '{name}' não existe."
            logger.error(msg)
            return msg
        
        try:
            logger.info(f"Executando ferramenta '{name}' com argumentos: {arguments}")
            # Injeta 'ui' se a função pedir (ajuste arquitetural de injeção de dependência)
            return self.callbacks[name](arguments, ui)
        except Exception as e:
            logger.exception(f"Erro interno ao executar a ferramenta '{name}'.")
            return f"Erro ao executar a ação: {str(e)}"

# ==============================================================================
# CÉREBRO DA ASSISTENTE (AGENTE PRINCIPAL)
# ==============================================================================
class TercaFeiraBrain:
    """Orquestrador Central da Assistente Virtual."""
    
    def __init__(self, config: Optional[BrainConfig] = None):
        self.config = config or BrainConfig()
        self.memory = MemoryManager(self.config)
        self.tool_registry = ToolRegistry()
        
        self._register_core_tools()

    def _register_core_tools(self):
        """Registra as ferramentas fundamentais do sistema."""
        
        # 1. Ferramenta: Controlar PC
        self.tool_registry.register_tool(
            name="controlar_pc",
            description="Controla o hardware local (volume, brilho, lixeira). NÃO use para abrir aplicativos.",
            parameters={
                "type": "object",
                "properties": {
                    "comando": {
                        "type": "string",
                        "description": "Comando exato. Ex: 'volume 80', 'limpar lixeira'."
                    }
                },
                "required": ["comando"]
            },
            callback=self._cb_controlar_pc
        )
        
        # 2. Ferramenta: Navegador/Pesquisa
        self.tool_registry.register_tool(
            name="abrir_site_ou_pesquisar",
            description="Abre sites ou pesquisa na internet.",
            parameters={
                "type": "object",
                "properties": {
                    "site_ou_termo": {
                        "type": "string",
                        "description": "Termo de busca ou nome do site. Ex: 'youtube', 'cotação do dólar hoje'."
                    }
                },
                "required": ["site_ou_termo"]
            },
            callback=self._cb_pesquisar
        )

        # 3. Ferramenta: Aplicativos (NOVA)
        self.tool_registry.register_tool(
            name="abrir_aplicativo",
            description="Abre programas e aplicativos locais instalados no computador (ex: calculadora, spotify, word, cmd).",
            parameters={
                "type": "object",
                "properties": {
                    "nome_app": {
                        "type": "string",
                        "description": "Nome do aplicativo. Ex: 'spotify', 'calculadora'."
                    }
                },
                "required": ["nome_app"]
            },
            callback=self._cb_abrir_app
        )

        # 4. Ferramenta: Música (NOVA)
        self.tool_registry.register_tool(
            name="tocar_musica",
            description="Toca músicas específicas no YouTube.",
            parameters={
                "type": "object",
                "properties": {
                    "nome_musica": {
                        "type": "string",
                        "description": "Nome da música ou artista."
                    }
                },
                "required": ["nome_musica"]
            },
            callback=self._cb_tocar_musica
        )

        # 5. Ferramenta: Responder
        self.tool_registry.register_tool(
            name="responder_usuario",
            description="Usa a voz para responder, informar ou conversar com o usuário. Sempre use no fim de uma ação.",
            parameters={
                "type": "object",
                "properties": {
                    "resposta_falada": {
                        "type": "string",
                        "description": "A frase em português natural que a assistente falará."
                    }
                },
                "required": ["resposta_falada"]
            },
            callback=self._cb_responder
        )
# 6. NOVA Ferramenta: Visão Computacional
        self.tool_registry.register_tool(
            name="analisar_monitor",
            description="Tira uma captura do ecrã do utilizador e usa visão computacional para descrever ou analisar o que está a ser exibido. Use sempre que o utilizador perguntar 'o que está no meu ecrã', 'leia este código', etc.",
            parameters={
                "type": "object",
                "properties": {
                    "pergunta_visual": {
                        "type": "string",
                        "description": "A instrução sobre o que analisar na imagem (ex: 'Resume o gráfico', 'Encontra o erro de código')."
                    }
                },
                "required": ["pergunta_visual"]
            },
            callback=lambda a, ui: analisar_tela(a.get('pergunta_visual', ''), ui)
        )

        # 7. NOVA Ferramenta: Executar Scripts Dinâmicos
        self.tool_registry.register_tool(
            name="executar_script_python",
            description="Escreve e executa código Python nativo no sistema do utilizador para automatizar tarefas (ex: organizar pastas, renomear ficheiros, cálculos complexos).",
            parameters={
                "type": "object",
                "properties": {
                    "codigo": {
                        "type": "string",
                        "description": "O código Python estritamente funcional a ser executado."
                    }
                },
                "required": ["codigo"]
            },
            callback=lambda a, ui: executar_codigo_ia(a.get('codigo', ''), ui)
        )
    # --- Callbacks das ferramentas ---
    
    def _cb_controlar_pc(self, args: Dict[str, Any], ui) -> str:
        comando = args.get("comando", "")
        ui.log(f"[AÇÃO DE SISTEMA] {comando}")
        controlar_hardware(comando, ui)
        salvar_lembranca(f"Ação no hardware executada: {comando}.")
        return f"Comando de PC '{comando}' executado com sucesso."

    def _cb_pesquisar(self, args: Dict[str, Any], ui) -> str:
        alvo = args.get("site_ou_termo", "")
        # O truque: Injetamos as palavras "abra o site" para o Regex do browser.py funcionar perfeitamente
        comando_injetado = f"abra o site {alvo}"
        handle_browser(comando_injetado, comando_injetado, ui)
        salvar_lembranca(f"Realizada navegação/pesquisa para: {alvo}.")
        return f"Ação de navegador/pesquisa para '{alvo}' realizada com sucesso."

    def _cb_abrir_app(self, args: Dict[str, Any], ui) -> str:
        nome_app = args.get("nome_app", "")
        # O truque: Injetamos a palavra "abra" para o Regex do application.py funcionar perfeitamente
        comando_injetado = f"abra {nome_app}"
        open_application(comando_injetado, ui)
        salvar_lembranca(f"Aplicativo aberto: {nome_app}.")
        return f"Aplicativo '{nome_app}' aberto com sucesso."

    def _cb_tocar_musica(self, args: Dict[str, Any], ui) -> str:
        nome_musica = args.get("nome_musica", "")
        # O truque: Injetamos as palavras "toca a música" para o Regex do music.py funcionar perfeitamente
        comando_injetado = f"toca a música {nome_musica}"
        play_music(comando_injetado, ui)
        salvar_lembranca(f"Música iniciada: {nome_musica}.")
        return f"Música '{nome_musica}' iniciada com sucesso."

    def _cb_responder(self, args: Dict[str, Any], ui) -> str:
        fala = args.get("resposta_falada", "Houve um problema ao processar a fala.")
        fala_limpa = fala.replace("*", "").replace("#", "")
        ui.log(f"\n[TERÇA FEIRA]: {fala_limpa}\n")
        speak(fala_limpa, ui)
        return "Resposta entregue ao usuário via TTS."

    # --- Lógica Principal do Agente ---
    
    def processar_comando(self, comando_usuario: str, ui) -> bool:
        """
        Inicia o Loop de Agente: analisa, planeja e executa (ReAct / Tool Loop).
        Retorna True caso o processo termine sem exceções fatais.
        """
        if not comando_usuario.strip():
            return True

        ui.log("[PROCESSAMENTO INICIADO] Consultando rede neural...")
        
        # Grava o comando do usuário no histórico permanente da sessão
        self.memory.append_message("user", comando_usuario)
        
        # Busca memória longa apenas para influenciar esta iteração (não polui history)
        lembrancas = buscar_contexto(comando_usuario)
        
        # Loop de Agente (Permite chamadas sequenciais, ex: pesquisa -> ler -> responder)
        for iteracao in range(self.config.max_agent_iterations):
            
            payload_messages = self.memory.build_prompt_payload(comando_usuario, lembrancas)
            
            payload = {
                "model": self.config.model,
                "messages": payload_messages,
                "tools": self.tool_registry.get_tools_schema(),
                "stream": False,
                "options": {
                    "temperature": self.config.temperature
                }
            }

            try:
                resposta = requests.post(self.config.ollama_url, json=payload, timeout=60)
                resposta.raise_for_status()
                
                dados = resposta.json()
                mensagem_ia = dados.get("message", {})
                
                # Caso 1: A IA chamou ferramentas
                if "tool_calls" in mensagem_ia and mensagem_ia["tool_calls"]:
                    
                    # Salva a intenção da IA de usar a ferramenta na memória
                    self.memory.history.append(mensagem_ia)
                    
                    for tool in mensagem_ia["tool_calls"]:
                        nome_funcao = tool["function"]["name"]
                        args_brutos = tool["function"]["arguments"]
                        
                        try:
                            # Parse robusto de argumentos malformados
                            args = args_brutos if isinstance(args_brutos, dict) else json.loads(args_brutos)
                        except json.JSONDecodeError:
                            logger.error(f"IA falhou ao gerar JSON para {nome_funcao}")
                            args = {}

                        # Executa a ferramenta mapeada
                        resultado_ferramenta = self.tool_registry.execute_tool(nome_funcao, args, ui)
                        
                        # Injeta o resultado da ferramenta de volta para a IA analisar (Obrigatório em FC)
                        self.memory.append_message("tool", resultado_ferramenta, tool_call_id=nome_funcao)
                        
                        # Se a ferramenta usada foi "responder_usuario", podemos encerrar o loop antecipadamente
                        if nome_funcao == "responder_usuario":
                            salvar_lembranca(f"Resumo da interação: O usuário pediu '{comando_usuario}' e a IA respondeu.")
                            return True
                            
                    # Após processar todas as ferramentas dessa iteração, o loop continua (vai chamar o Ollama de novo)
                    continue
                
                # Caso 2: A IA não chamou ferramentas, respondeu em texto puro (Fallback)
                texto_final = mensagem_ia.get("content", "").strip()
                if texto_final:
                    # Força a resposta via TTS mesmo que a IA tenha esquecido de usar a ferramenta 'responder_usuario'
                    self.tool_registry.execute_tool("responder_usuario", {"resposta_falada": texto_final}, ui)
                    self.memory.append_message("assistant", texto_final)
                    salvar_lembranca(f"Usuário: {comando_usuario} | Terça Feira: {texto_final}")
                    return True
                
            except requests.exceptions.ConnectionError:
                erro_msg = "[ERRO CRÍTICO] Servidor Ollama offline ou inacessível."
                ui.log(erro_msg)
                speak("Meu servidor cognitivo parece estar offline. Por favor, verifique o sistema.", ui)
                return False
            except requests.exceptions.Timeout:
                erro_msg = "[ERRO CRÍTICO] O processamento neural demorou demais."
                ui.log(erro_msg)
                speak("O processamento está muito lento e atingiu o limite de tempo.", ui)
                return False
            except Exception as e:
                logger.exception("Falha na malha de processamento.")
                ui.log(f"[ERRO DO SISTEMA] {str(e)}")
                return False

        # Se ultrapassar o limite de iterações do agente:
        ui.log("[ALERTA] Limite de raciocínio da IA atingido.")
        speak("Acho que me perdi na linha de pensamento, podemos tentar novamente?", ui)
        return False


# ==============================================================================
# INSTÂNCIA GLOBAL E WRAPPER DE COMPATIBILIDADE (Não quebra o main.py atual)
# ==============================================================================
_cerebro_instancia = TercaFeiraBrain()

def process_command_autonomo(comando: str, ui) -> bool:
    """
    Função Wrapper para manter a compatibilidade com main.py.
    Repassa o comando para o novo orquestrador orientado a objetos.
    """
    return _cerebro_instancia.processar_comando(comando, ui)