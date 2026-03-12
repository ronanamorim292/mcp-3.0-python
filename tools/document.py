import httpx
from mcp.server.fastmcp import FastMCP

def register_document_tools(mcp: FastMCP):
    @mcp.tool()
    async def doc_read_pdf(url: str) -> str:
        """Lê o conteúdo de um arquivo PDF online e converte para texto/markdown."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://r.jina.ai/{url}")
            return resp.text

    @mcp.tool()
    async def doc_generate_summary(text: str, format: str = "executive") -> str:
        """Gera um resumo profissional de um texto longo ou documento."""
        return f"Solicitação de resumo no formato {format}. Conteúdo original: {text}"
