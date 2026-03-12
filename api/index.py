import os
import sys

# Ajustar PYTHONPATH
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport

load_dotenv()

# Inicializar FastMCP
mcp = FastMCP("MCP-3.0")

# Carregar ferramentas (com tratamento de erro individual)
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
        load_errors.append(f"{module_name}: {str(e)}")

# Configurar transporte SSE
# Importante: O endereço de mensagens DEVE ser absoluto ou compatível com a Vercel
sse = SseServerTransport("/api/messages") 

async def handle_sse(request):
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await mcp.server.run_async(read_stream, write_stream)
    except Exception as e:
        return JSONResponse({"error": "SSE connection failed", "details": str(e)}, status_code=500)

async def handle_messages(request):
    try:
        await sse.handle_post_messages(request.scope, request.receive, request._send)
    except Exception as e:
        return JSONResponse({"error": "Message delivery failed", "details": str(e)}, status_code=500)

async def index_route(request):
    return JSONResponse({
        "status": "online",
        "load_errors": load_errors,
        "mcp_ready": True,
        "available_tools": [t.name for t in mcp.list_tools()] if not load_errors else "too_many_to_list"
    })

# Criar App Starlette com CORS
app = Starlette(debug=True, routes=[
    Route("/", index_route),
    Route("/sse", handle_sse, methods=["GET"]),
    Route("/mcp", handle_sse, methods=["GET"]),
    Route("/api/messages", handle_messages, methods=["POST"]),
    Route("/messages", handle_messages, methods=["POST"]), # Alias extra
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
