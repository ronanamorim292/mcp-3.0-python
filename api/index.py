import os
import sys

# Ajustar PYTHONPATH para Vercel encontrar a pasta 'tools'
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from mcp.server.sse import SseServerTransport

load_dotenv()

# Inicializar FastMCP
mcp = FastMCP("MCP-3.0")

# Lista de módulos de ferramentas
tool_modules = [
    "tools.api", "tools.easypanel", "tools.github", "tools.appwrite",
    "tools.n8n", "tools.evolution", "tools.system", "tools.search",
    "tools.mercadopago", "tools.calendar", "tools.email", "tools.document",
    "tools.memory", "tools.secrets"
]

load_errors = []
for module_name in tool_modules:
    try:
        module = __import__(module_name, fromlist=["*"])
        short_name = module_name.split(".")[-1]
        func_name = f"register_{short_name}_tools"
        if short_name == "mercadopago": func_name = "register_mp_tools"
        register_func = getattr(module, func_name, None)
        if register_func: register_func(mcp)
    except Exception as e:
        load_errors.append(f"Erro em {module_name}: {str(e)}")

# Configurar o transporte SSE explicitamente para evitar confusão de rotas
sse = SseServerTransport("/messages")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp.server.run_async(read_stream, write_stream)

async def handle_messages(request):
    await sse.handle_post_messages(request.scope, request.receive, request._send)

async def index_route(request):
    return JSONResponse({
        "status": "online",
        "load_errors": load_errors,
        "endpoints": ["/sse", "/mcp", "/messages"]
    })

# Definir as rotas de forma explícita e manual para garantir que a Vercel as veja
routes = [
    Route("/", index_route),
    Route("/sse", handle_sse, methods=["GET"]),
    Route("/mcp", handle_sse, methods=["GET"]),
    Route("/messages", handle_messages, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)
