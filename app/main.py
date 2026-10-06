"""Ejecución asíncrona de la demostración y generación de la traza."""

import asyncio
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver

from app.graph import build_graph

ROOT = Path(__file__).resolve().parent.parent


def serializar_evento(evento: dict[str, Any]) -> dict[str, Any]:
    """Reduce un evento LangGraph a campos JSON legibles para la entrega."""
    salida: dict[str, Any] = {}
    for nodo, datos in evento.items():
        mensajes = datos.get("messages", [])
        salida[nodo] = [mensaje.model_dump(mode="json") for mensaje in mensajes]
    return salida


async def ejecutar_demo() -> None:
    """Corre el grafo fuera del event loop y guarda la traza ReAct resultante."""
    load_dotenv(ROOT / ".env")
    configuracion = {"configurable": {"thread_id": "cliente-102"}, "recursion_limit": 10}
    consulta = "¿Cuántos pedidos tuvo el cliente 102, cuál fue el total y cuál fue el último?"

    # SqliteSaver es síncrono; asyncio.to_thread mantiene la aplicación asíncrona.
    with SqliteSaver.from_conn_string(str(ROOT / "checkpoints.sqlite")) as memoria:
        agente = build_graph(memoria)
        eventos = await asyncio.to_thread(
            lambda: list(agente.stream({"messages": [HumanMessage(content=consulta)]}, configuracion))
        )
        seguimiento = await asyncio.to_thread(
            lambda: agente.invoke(
                {"messages": [HumanMessage(content="¿y el último?")]}, configuracion
            )
        )

    traza = {
        "thread_id": "cliente-102",
        "consulta": consulta,
        "eventos": [serializar_evento(evento) for evento in eventos],
        "respuesta_con_memoria": seguimiento["messages"][-1].content,
    }
    (ROOT / "traces" / "ejecucion.json").write_text(
        json.dumps(traza, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(traza["respuesta_con_memoria"])


if __name__ == "__main__":
    asyncio.run(ejecutar_demo())
