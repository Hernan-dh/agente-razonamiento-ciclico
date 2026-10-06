"""Herramientas que el modelo puede decidir usar."""

from typing import Final

from langchain_core.tools import tool

PEDIDOS: Final[dict[int, list[dict[str, object]]]] = {
    102: [
        {"id": 9001, "fecha": "2025-02-10", "total": 4500},
        {"id": 9002, "fecha": "2025-03-04", "total": 5000},
        {"id": 9003, "fecha": "2025-03-18", "total": 5000},
    ]
}


@tool
def buscar_resumen_pedidos(cliente_id: int) -> dict[str, int | str]:
    """Consulta el resumen de pedidos de un cliente en la base de datos simulada.

    Usala cuando el usuario pida cuántos pedidos tuvo un cliente o el importe
    total acumulado. Recibe el identificador numérico del cliente y devuelve la
    cantidad de pedidos y su total. No devuelve el detalle del último pedido;
    para eso usá buscar_ultimo_pedido en una llamada separada.
    """
    pedidos = PEDIDOS.get(cliente_id, [])
    return {
        "cliente_id": cliente_id,
        "pedidos": len(pedidos),
        "total": sum(int(pedido["total"]) for pedido in pedidos),
    }


@tool
def buscar_ultimo_pedido(cliente_id: int) -> dict[str, int | str | None]:
    """Obtiene exclusivamente el pedido más reciente de un cliente.

    Usala cuando el usuario solicite el último pedido, su fecha o su importe.
    Recibe el identificador numérico del cliente. Si no hay pedidos, devuelve
    encontrado=false; si existe, devuelve id, fecha y total. Esta herramienta no
    ofrece el total histórico ni la cantidad de pedidos.
    """
    pedidos = PEDIDOS.get(cliente_id, [])
    if not pedidos:
        return {"cliente_id": cliente_id, "encontrado": False}
    ultimo = pedidos[-1]
    return {"cliente_id": cliente_id, "encontrado": True, **ultimo}
