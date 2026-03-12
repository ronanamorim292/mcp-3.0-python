import os
import sys
import logging
import traceback
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Ajustar PYTHONPATH
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

load_dotenv(os.path.join(root_path, ".env"))

mcp = FastMCP("MCP-3-0")

# Importar ferramentas
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

# Criar app Starlette
starlette_app = Starlette()

# Middleware para desativar buffering no EasyPanel/Traefik
@starlette_app.middleware("http")
async def add_mcp_headers(request, call_next):
    response = await call_next(request)
    if request.url.path in ["/sse", "/mcp", "/messages"]:
        response.headers["x-accel-buffering"] = "no"
        response.headers["cache-control"] = "no-cache, no-store, must-revalidate"
        response.headers["connection"] = "keep-alive"
    return response

starlette_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@starlette_app.route("/sse")
@starlette_app.route("/mcp")
async def handle_sse(request):
    return await mcp.handle_sse(request)

@starlette_app.route("/messages", methods=["POST"])
async def handle_messages(request):
    return await mcp.handle_messages(request)

@starlette_app.route("/")
async def index_route(request):
    tools = await mcp.list_tools()
    return JSONResponse({
        "status": "online",
        "tools": len(tools),
        "msg": "Use /sse ou /mcp para conectar"
    })

# O app final é o Starlette configurado para rodar no Uvicorn
app = starlette_app
