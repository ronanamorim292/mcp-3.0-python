from mcp.server.fastmcp import FastMCP
import os
import httpx
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar FastMCP
mcp = FastMCP("MCP-3.0")

# Importar ferramentas (serão definidas em arquivos separados para organização)
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

if __name__ == "__main__":
    mcp.run()
