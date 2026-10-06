"""Definición del StateGraph ReAct con persistencia SQLite."""

import os
from typing import Any

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.tools import buscar_resumen_pedidos, buscar_ultimo_pedido

TOOLS = [buscar_resumen_pedidos, buscar_ultimo_pedido]


class AgentState(MessagesState):
    """Estado inmutable: MessagesState acumula mensajes mediante su reducer."""


SYSTEM_PROMPT = """Sos un asistente de atención de pedidos.
Decidí autónomamente si necesitás una herramienta según la consulta.
Para datos de pedidos, nunca inventes información: usá las herramientas.
Si falta el id de cliente o los resultados son insuficientes, pedí aclaración.
Cuando una consulta requiere cantidad/total y último pedido, llamá ambas
herramientas antes de responder. Recordá el contexto de la conversación."""


def build_graph(checkpointer: SqliteSaver) -> Any:
    """Construye el grafo modelo → herramientas → modelo y conecta su memoria."""
    model = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0
    ).bind_tools(TOOLS)

    def call_model(state: AgentState) -> dict[str, list]:
        response = model.invoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
        return {"messages": [response]}

    workflow = StateGraph(AgentState)
    workflow.add_node("model", call_model)
    workflow.add_node("tools", ToolNode(TOOLS))
    workflow.set_entry_point("model")
    workflow.add_conditional_edges("model", tools_condition, {"tools": "tools", END: END})
    workflow.add_edge("tools", "model")
    return workflow.compile(checkpointer=checkpointer)
