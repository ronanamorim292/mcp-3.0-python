from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar FastMCP com transporte SSE para Web
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

# Interface ASGI para a Vercel
from mcp.server.fastmcp import Context
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from mcp.server.sse import SseServerTransport

app = Starlette()
sse = SseServerTransport("/sse")

@app.route("/")
async def index(request):
    return JSONResponse({"status": "online", "message": "MCP-3.0 Python Server is running", "endpoints": ["/sse"]})

@app.route("/sse", methods=["GET", "POST"])
async def handle_sse(request):
    if request.method == "POST":
        return await sse.handle_post_messages(request.scope, request.receive, request._send)
    
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
        await mcp.server.run_async(read_stream, write_stream)

# Exportar a app para a Vercel
# Nota: Como o FastMCP é novo, essa implementação pode variar conforme a versão.
# Se a Vercel não detectar, usaremos a abordagem de subir o servidor stdio via subprocess.
