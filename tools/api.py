import httpx
from mcp.server.fastmcp import FastMCP

def register_api_tools(mcp: FastMCP):
    @mcp.tool()
    async def api_generic_request(
        url: str, 
        method: str = "GET", 
        data: dict = None, 
        headers: dict = None
    ) -> str:
        """Fazer uma requisição HTTP REST genérica."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    headers=headers
                )
                response.raise_for_status()
                return str(response.json())
            except Exception as e:
                return f"Erro na requisição API: {str(e)}"
