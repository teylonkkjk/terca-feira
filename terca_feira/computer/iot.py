"""
Módulo de Integração IoT e Sandbox de Execução.
"""
import requests
import subprocess
import tempfile
import os
import logging

logger = logging.getLogger("TercaFeira.IoT")

class SmartEnvironment:
    
    @staticmethod
    def controlar_luzes(comando: str, ui) -> str:
        """
        Exemplo de webhook local para Smart Home (Home Assistant, Tasmota, etc).
        Ajuste as URLs consoante os IPs dos seus dispositivos reais.
        """
        ui.log(f"[IoT] A acionar protocolo de ambiente: {comando}")
        # Exemplo de lógica (Substitua pelos seus endpoints reais)
        try:
            # if "desligar" in comando:
            #    requests.get("http://192.168.1.50/cm?cmnd=Power%20Off", timeout=2)
            return f"Comando IoT '{comando}' enviado para a rede local."
        except Exception as e:
            logger.error(f"Falha na rede IoT: {e}")
            return "Erro ao contactar dispositivos da casa."

    @staticmethod
    def executar_script_seguro(codigo_python: str, ui) -> str:
        """
        Cria um ficheiro Python temporário, executa o código que a IA escreveu,
        captura o resultado e apaga o ficheiro (Sandbox básica).
        """
        ui.log("[SANDBOX] A executar guião (script) dinâmico...")
        
        # Cria um ficheiro temporário no sistema
        fd, caminho_temp = tempfile.mkstemp(suffix=".py")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(codigo_python)
            
            # Executa o código e aguarda o resultado (Timeout de 10s por segurança)
            resultado = subprocess.run(["python", caminho_temp], capture_output=True, text=True, timeout=10)
            
            saida = resultado.stdout if resultado.returncode == 0 else resultado.stderr
            return f"Resultado da execução do script:\n{saida.strip()}"
            
        except subprocess.TimeoutExpired:
            return "Erro: A execução do script demorou demasiado tempo e foi cancelada."
        except Exception as e:
            return f"Erro na execução da Sandbox: {e}"
        finally:
            # Limpa os rastos independentemente do resultado
            os.remove(caminho_temp)

def acionar_iot(comando: str, ui) -> str:
    return SmartEnvironment.controlar_luzes(comando, ui)

def executar_codigo_ia(codigo: str, ui) -> str:
    return SmartEnvironment.executar_script_seguro(codigo, ui)