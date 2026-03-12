import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-server")

# Ajustar PYTHONPATH
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

load_dotenv(os.path.join(root_path, ".env"))

# Inicializar FastMCP
mcp = FastMCP("MCP-3-0")

# Importar e registrar ferramentas
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
        if hasattr(m, func):
            getattr(m, func)(mcp)
            logger.info(f"Ferramentas registradas: {module}")
    except Exception as e:
        logger.error(f"Erro ao registrar {module}: {e}")

# Criar App FastAPI para maior controle sobre headers e rota
app = FastAPI()

# Permissão total de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rota de status (Sanity Check)
@app.get("/")
async def index_route(request: Request):
    tools = await mcp.list_tools()
    return {
        "status": "online",
        "tools": len(tools),
        "protocol": "mcp/sse",
        "client_host": request.client.host if request.client else "unknown"
    }

# Handler Universal para MCP (SSE e Messages)
# Esta função intercepta a requisição e limpa cabeçalhos que podem causar "Invalid Host header"
async def mcp_proxy_handler(request: Request):
    mcp_sse_app = mcp.sse_app()
    
    # Clonar o scope para não afetar outras rotas
    scope = dict(request.scope)
    
    # Hack: Limpar ou forçar o cabeçalho Host para evitar 421 Misdirected Request/Invalid Host
    new_headers = []
    for k, v in scope.get('headers', []):
        if k.lower() == b'host':
            # Forçamos o host para condizer com o que o server interno espera se necessário
            # Ou apenas deixamos passar se o check for removido
            new_headers.append((b'host', b'localhost'))
        else:
            new_headers.append((k, v))
    scope['headers'] = new_headers
    
    # Chama a app interna do FastMCP
    return await mcp_sse_app(scope, request.receive, request.send)

# Rotas MCP
@app.get("/sse")
async def sse_route(request: Request):
    return await mcp_proxy_handler(request)

@app.post("/messages")
async def messages_post(request: Request):
    return await mcp_proxy_handler(request)

@app.get("/messages")
async def messages_get(request: Request):
    return await mcp_proxy_handler(request)

# Aliases
@app.get("/mcp")
async def mcp_alias(request: Request):
    return await mcp_proxy_handler(request)

@app.middleware("http")
async def add_anti_buffering_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if any(p in path for p in ["sse", "mcp", "messages"]):
        response.headers["x-accel-buffering"] = "no"
        response.headers["cache-control"] = "no-cache, no-store, must-revalidate"
        response.headers["connection"] = "keep-alive"
        # Garante que o content-type de SSE não seja alterado
        if "sse" in path or "mcp" in path:
            response.headers["content-type"] = "text/event-stream"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
