import operator
from typing import Annotated, TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph


class AgentState(TypedDict):
    messages: Annotated[list[dict[str, str]], operator.add]


llm = ChatOllama(model='gemma4:e4b')


async def default_respond_node(state: AgentState) -> dict:
    messages_history = state['messages']

    response = await llm.ainvoke(messages_history)

    return {'messages': [response]}


workflow = StateGraph(AgentState)

workflow.add_node('responder', default_respond_node)

workflow.add_edge(START, 'responder')
workflow.add_edge('responder', END)

graph = workflow.compile()
