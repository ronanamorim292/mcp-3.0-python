import os
import sys
import logging
import traceback

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

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
        logger.info(f"Ferramentas registradas: {module}")
    except Exception as e:
        logger.error(f"Erro ao registrar {module}: {e}")

# Transporte SSE Manual
sse = SseServerTransport("/messages")

async def handle_sse(scope, receive, send):
    try:
        # O parametro sse.connect_sse gerencia o fluxo de stream
        logger.info("Nova conexão SSE iniciada")
        async with sse.connect_sse(scope, receive, send) as (read_stream, write_stream):
            # No FastMCP, o servidor real fica em _server
            await mcp._server.run_async(read_stream, write_stream)
    except Exception as e:
        logger.error(f"Erro Crítico no SSE: {e}")
        logger.error(traceback.format_exc())
        # Tentar enviar um erro se o stream não tiver começado
        try:
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"text/plain")],
            })
            await send({ "type": "http.response.body", "body": str(e).encode() })
        except: pass

async def handle_messages(scope, receive, send):
    logger.info("Nova mensagem POST recebida em /messages")
    await sse.handle_post_messages(scope, receive, send)

async def index_route(request):
    tools = await mcp.list_tools()
    return JSONResponse({
        "status": "online",
        "tools": len(tools),
        "msg": "Use /sse ou /mcp para conectar"
    })

starlette_app = Starlette(
    routes=[
        Route("/", index_route),
    ]
)

starlette_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        await starlette_app(scope, receive, send)
        return
    
    if scope["type"] == "http":
        path = scope["path"]
        if path in ["/sse", "/mcp"]:
            await handle_sse(scope, receive, send)
        elif path == "/messages":
            await handle_messages(scope, receive, send)
        else:
            await starlette_app(scope, receive, send)
    else:
        await starlette_app(scope, receive, send)
