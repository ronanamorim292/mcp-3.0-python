import os
import sys
import logging
import traceback
from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
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

# Obter a aplicação Starlette oficial do FastMCP que já tem os handlers SSE
app = mcp.sse_app()

# Adicionar Middleware de Headers para estabilidade no EasyPanel (Anti-Buffering)
@app.middleware("http")
async def add_mcp_headers(request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path in ["/sse", "/mcp", "/messages"]:
        response.headers["x-accel-buffering"] = "no"
        response.headers["cache-control"] = "no-cache, no-store, must-revalidate"
        response.headers["connection"] = "keep-alive"
    return response

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar alias /mcp para o endpoint /sse
try:
    sse_route = next(r for r in app.routes if getattr(r, 'path', None) == "/sse")
    app.add_route("/mcp", sse_route.endpoint, methods=["GET"])
except Exception as e:
    logger.warning(f"Não foi possível criar alias /mcp: {e}")

# Adicionar rota de índice informativa
@app.route("/")
async def index_route(request):
    tools = await mcp.list_tools()
    return JSONResponse({
        "status": "online",
        "tools": len(tools),
        "protocol": "mcp/sse",
        "endpoints": {
            "sse": "/sse",
            "mcp_alias": "/mcp",
            "messages": "/messages"
        }
    })

# Exportar 'app' para o Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
