import os
import sys

# Forçar o caminho raiz do projeto no PYTHONPATH para a Vercel encontrar a pasta 'tools'
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(current_dir)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carregar o .env se ele existir (na Vercel ele usará as variáveis de ambiente do sistema)
load_dotenv(os.path.join(root_path, ".env"))

# Inicializar o servidor MCP
mcp = FastMCP("mcp-3-0-python")

# Adicionar uma ferramenta de teste rápido para validar conexões
@mcp.tool()
async def ping() -> str:
    """Ferramenta de teste para verificar se o servidor online está respondendo."""
    return "pong! O servidor online está funcionando perfeitamente."

# Carregar os módulos de ferramentas
tool_modules = [
    "tools.api", "tools.easypanel", "tools.github", "tools.appwrite",
    "tools.n8n", "tools.evolution", "tools.system", "tools.search",
    "tools.mercadopago", "tools.calendar", "tools.email", "tools.document",
    "tools.memory", "tools.secrets"
]

for module_name in tool_modules:
    try:
        module = __import__(module_name, fromlist=["*"])
        short_name = module_name.split(".")[-1]
        func_name = f"register_{short_name}_tools"
        if short_name == "mercadopago": func_name = "register_mp_tools"
        register_func = getattr(module, func_name, None)
        if register_func:
            register_func(mcp)
    except Exception as e:
        print(f"Aviso: Não foi possível carregar {module_name}: {e}")

# Gerar a aplicação SSE nativa do FastMCP
mcp_app = mcp.sse_app()

# Criar uma rota de status amigável
async def index_route(request):
    tools = await mcp.list_tools()
    return JSONResponse({
        "status": "online",
        "service": "MCP-3.0 Python (Vercel)",
        "tools_loaded": len(tools),
        "endpoints": ["/sse", "/messages", "/mcp"]
    })

# Rota alias para /mcp que usa o mesmo motor do /sse
async def mcp_alias(request):
    return await mcp_app(request.scope, request.receive, request._send)

# Montar a aplicação final unindo tudo
app = Starlette(
    routes=[
        Route("/", index_route),
        Route("/mcp", mcp_alias, methods=["GET", "POST"]),
        Mount("/", mcp_app) # Monta /sse e /messages automaticamente
    ]
)

# Adicionar CORS para o n8n e outras plataformas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
