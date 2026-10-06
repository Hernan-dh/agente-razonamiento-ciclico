# Agente de razonamiento cíclico con memoria persistente

Implementación mínima de un agente ReAct para la pre-entrega 5. El modelo decide
cuándo usar herramientas mediante `bind_tools`; no hay rutas manuales según el
texto de la consulta.

## Requisitos

- Python 3.12 o superior
- Poetry
- Una clave de OpenAI

## Instalación y ejecución

```bash
poetry install
copy .env.example .env
# Editar .env y completar OPENAI_API_KEY
poetry run python -m app.main
```

La ejecución crea `checkpoints.sqlite` y reemplaza `traces/ejecucion.json` con
la traza real. El ejemplo versionado en esa carpeta muestra el ciclo esperado.

## Diseño

`AgentState` hereda de `MessagesState`, que acumula mensajes usando su reducer.
El grafo conecta `model → tools → model`: `tools_condition` decide si continúa
al nodo `ToolNode` o finaliza. Las dos herramientas tienen responsabilidades
separadas, por lo que la consulta demostrativa requiere dos llamadas.

`SqliteSaver` guarda los checkpoints con `thread_id="cliente-102"`. La segunda
consulta de la demo reutiliza ese identificador y por eso conserva el contexto.
La aplicación se inicia con `asyncio.run`; dado que `SqliteSaver` es síncrono,
las invocaciones se realizan con `asyncio.to_thread` para no bloquear el loop.
Todas las invocaciones establecen `recursion_limit=10`.

## Traza incluida

Ver [traces/ejecucion.json](traces/ejecucion.json). Contiene la consulta, las
dos llamadas a herramienta, la respuesta final y una consulta posterior con el
mismo `thread_id`.
