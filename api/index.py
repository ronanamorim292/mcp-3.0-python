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
from starlette.routing import Route, Mount

load_dotenv()

# Inicializar FastMCP
mcp = FastMCP("MCP-3.0")

# Lista de módulos de ferramentas para carregar com segurança
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
        # Cada módulo deve ter uma função register_..._tools(mcp)
        # O nome da função segue o padrão: register_{nome_do_arquivo}_tools
        short_name = module_name.split(".")[-1]
        # Mapeamento manual para nomes que não seguem o padrão exato se houver
        func_name = f"register_{short_name}_tools"
        if short_name == "mercadopago": func_name = "register_mp_tools"
        
        register_func = getattr(module, func_name, None)
        if register_func:
            register_func(mcp)
        else:
            load_errors.append(f"Função {func_name} não encontrada em {module_name}")
    except Exception as e:
        load_errors.append(f"Erro ao carregar {module_name}: {str(e)}")

# Se houver erros graves, vamos reportar na rota raiz
@mcp.tool()
async def health_check() -> str:
    """Verificar o status do servidor e ferramentas."""
    if not load_errors:
        return "Todos os módulos carregados com sucesso."
    return "Erros detectados:\n" + "\n".join(load_errors)

# Obter a aplicação SSE nativa
mcp_sse_app = mcp.sse_app()

async def index_route(request):
    return JSONResponse({
        "status": "online" if not load_errors else "degraded",
        "service": "MCP-3.0 Python",
        "load_errors": load_errors,
        "endpoints": ["/sse", "/messages", "/mcp"]
    })

async def mcp_alias(request):
    return await mcp_sse_app(request.scope, request.receive, request._send)

app = Starlette(routes=[
    Route("/", index_route),
    Route("/mcp", mcp_alias, methods=["GET", "POST"]),
    Mount("/", mcp_sse_app)
])
