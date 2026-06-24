import importlib
from typing import Protocol

from langgraph.graph.state import CompiledStateGraph


class AgentGraphLoaderProtocol(Protocol):
    """
    Protocolo que define o comportamento de um carregador de grafos.
    Qualquer função ou classe que receba o nome do agente e retorne
    o grafo cumpre este protocolo.
    """

    def __call__(self, agent_name: str) -> CompiledStateGraph: ...


def get_agent_graph(agent_name: str) -> CompiledStateGraph:
    """Carrega dinamicamente o grafo compilado (LangGraph)."""
    module_path = f'llm.agents.{agent_name.lower().replace(" ", "_")}'

    try:
        module = importlib.import_module(module_path)
        return getattr(module, 'graph')
    except (ModuleNotFoundError, AttributeError) as e:
        raise RuntimeError(f'Falha ao carregar o agente {agent_name}: {e}')
