import os
import sys

# Ajustar PYTHONPATH
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport
from dotenv import load_dotenv

load_dotenv(os.path.join(root_path, ".env"))

mcp = FastMCP("MCP-3-0")

# Importar ferramentas (Silenciosamente)
tool_modules = [
    "tools.api", "tools.easypanel", "tools.github", "tools.appwrite",
    "tools.n8n", "tools.evolution", "tools.system", "tools.search",
    "tools.mercadopago", "tools.calendar", "tools.email", "tools.document",
    "tools.memory", "tools.secrets"
]

for module in tool_modules:
    try:
        m = __import__(module, fromlist=["*"])
        short = module.split(".")[-1]
        func = f"register_{short}_tools"
        if short == "mercadopago": func = "register_mp_tools"
        getattr(m, func)(mcp)
    except: pass

# Transporte SSE Manual (Mais estável para Vercel)
sse = SseServerTransport("/messages")

async def handle_sse(request):
    # O parametro sse.connect_sse gerencia o fluxo de stream
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp.server.run_async(read_stream, write_stream)

async def handle_messages(request):
    await sse.handle_post_messages(request.scope, request.receive, request._send)

async def index_route(request):
    tools = await mcp.list_tools()
    return JSONResponse({
        "status": "online",
        "tools": len(tools),
        "msg": "Use /sse ou /mcp para conectar"
    })

app = Starlette(
    routes=[
        Route("/", index_route),
        Route("/sse", handle_sse),
        Route("/mcp", handle_sse),
        Route("/messages", handle_messages, methods=["POST"]),
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
