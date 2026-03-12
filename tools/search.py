import httpx
from mcp.server.fastmcp import FastMCP

def register_search_tools(mcp: FastMCP):
    @mcp.tool()
    async def search_web(query: str, max_results: int = 5) -> str:
        """Realiza uma busca na web usando DuckDuckGo e retorna os principais resultados."""
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            data = resp.json()
            
            results = [f"Resultados para: '{query}'\n"]
            if data.get("AbstractText"):
                results.append(f"--- RESUMO ---\n{data['AbstractText']}\nLink: {data.get('AbstractURL')}\n")
            
            topics = data.get("RelatedTopics", [])[:max_results]
            if topics:
                results.append("--- LINKS RELACIONADOS ---")
                for i, topic in enumerate(topics):
                    if "Text" in topic and "FirstURL" in topic:
                        results.append(f"{i+1}. {topic['Text']}\n   URL: {topic['FirstURL']}")
            
            return "\n".join(results) if len(results) > 1 else "Nenhum resultado encontrado."

    @mcp.tool()
    async def search_get_page_content(url: str) -> str:
        """Extrai o conteúdo de texto de uma URL específica (Web Scraping simples)."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"https://r.jina.ai/{url}")
            return resp.text
