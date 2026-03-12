import os
import sys

# Garantir que a pasta raiz esteja no PYTHONPATH para encontrar a pasta 'tools'
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar FastMCP
mcp = FastMCP("MCP-3.0")

# Importar registros de ferramentas
from tools.api import register_api_tools
from tools.easypanel import register_easypanel_tools
from tools.github import register_github_tools
from tools.appwrite import register_appwrite_tools
from tools.n8n import register_n8n_tools
from tools.evolution import register_evolution_tools
from tools.system import register_system_tools
from tools.search import register_search_tools
from tools.mercadopago import register_mp_tools
from tools.calendar import register_calendar_tools
from tools.email import register_email_tools
from tools.document import register_document_tools
from tools.memory import register_memory_tools
from tools.secrets import register_secrets_tools

# Registrar todas as ferramentas
register_api_tools(mcp)
register_easypanel_tools(mcp)
register_github_tools(mcp)
register_appwrite_tools(mcp)
register_n8n_tools(mcp)
register_evolution_tools(mcp)
register_system_tools(mcp)
register_search_tools(mcp)
register_mp_tools(mcp)
register_calendar_tools(mcp)
register_email_tools(mcp)
register_document_tools(mcp)
register_memory_tools(mcp)
register_secrets_tools(mcp)

# Obter a aplicação SSE nativa do FastMCP
mcp_sse_app = mcp.sse_app()

# Criar a aplicação principal para incluir uma rota raiz amigável
async def index_route(request):
    return JSONResponse({
        "status": "online",
        "service": "MCP-3.0 Python",
        "endpoints": ["/sse", "/messages", "/mcp"]
    })

# Rota alias para /mcp que aponta para o mesmo handler do /sse
async def mcp_alias(request):
    # Encaminha a requisição para o app do MCP
    return await mcp_sse_app(request.scope, request.receive, request._send)

app = Starlette(routes=[
    Route("/", index_route),
    Route("/mcp", mcp_alias, methods=["GET", "POST"]),
    Mount("/", mcp_sse_app)
])
