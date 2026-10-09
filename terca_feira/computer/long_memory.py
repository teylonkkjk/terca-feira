"""
long_memory.py - Módulo de Memória de Longo Prazo (Vector Database).
"""

import logging
import uuid
import chromadb
from chromadb.config import Settings

logger = logging.getLogger("TercaFeira.LongMemory")

class VectorMemoryManager:
    def __init__(self):
        self.colecao = None
        self._inicializado = False

    def _inicializar(self):
        if self._inicializado: return
        try:
            cfg = Settings(anonymized_telemetry=False)
            cliente = chromadb.PersistentClient(path="./memoria_vetorial", settings=cfg)
            self.colecao = cliente.get_or_create_collection(name="memoria_terca_feira")
            self._inicializado = True
            logger.info("Banco de vetores online.")
        except Exception as e:
            logger.error(f"FALHA AO CARREGAR CHROMADB: {e}")
            self.colecao = None

    def salvar(self, texto: str) -> None:
        self._inicializar()
        if not self.colecao or len(texto.strip()) < 15: return
        try:
            self.colecao.add(documents=[texto], ids=[str(uuid.uuid4())])
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")

    def buscar(self, pergunta: str) -> str:
        self._inicializar()
        if not self.colecao: return ""
        try:
            total = self.colecao.count()
            if total == 0: return ""
            res = self.colecao.query(query_texts=[pergunta], n_results=min(3, total))
            docs = res.get("documents", [[]])
            if docs and docs[0]:
                return "\n[LEMBRANÇAS DO PASSADO]:\n" + "\n".join(docs[0])
        except Exception as e:
            logger.error(f"Erro na busca vetorial: {e}")
        return ""

_memoria = VectorMemoryManager()

def salvar_lembranca(texto: str) -> None:
    _memoria.salvar(texto)

def buscar_contexto(pergunta: str) -> str:
    return _memoria.buscar(pergunta)