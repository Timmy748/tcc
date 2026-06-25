from abc import abstractmethod
from typing import Protocol, override

from api.dtos.message_dto import MessageDTO
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import RunnableConfig

from llm.get_agent_graph import get_agent_graph


class AgentHandlerInterface(Protocol):
    @abstractmethod
    async def executar_interacao(
        self,
        chat_id: int,
        chat_history: list[MessageDTO],
        user_message: str,
        agent_name: str,
    ): ...


class AgentHandler(AgentHandlerInterface):
    @override
    async def executar_interacao(
        self,
        chat_id: int,
        chat_history: list[MessageDTO],
        user_message: str,
        agent_name: str,
    ):
        messages = [
            HumanMessage(content=msg['content'])
            if msg['sender_type'] == 'USER'
            else AIMessage(content=msg['content'])
            for msg in chat_history
        ]
        messages.append(HumanMessage(content=user_message))

        config: RunnableConfig = {'configurable': {'thread_id': str(chat_id)}}

        graph = get_agent_graph(agent_name)
        result = await graph.ainvoke({'messages': messages}, config=config)
        last_ai_message = result['messages'][-1].content

        return last_ai_message
