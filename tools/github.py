import httpx
import os
import json
import base64
from mcp.server.fastmcp import FastMCP

def register_github_tools(mcp: FastMCP):
    token = os.getenv("GITHUB_TOKEN")
    
    def get_headers():
        if not token: return None
        return {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    @mcp.tool()
    async def github_list_repos() -> str:
        """Listar todos os seus repositórios no GitHub."""
        headers = get_headers()
        if not headers: return "GitHub não configurado."
        
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://api.github.com/user/repos?sort=updated&per_page=50", headers=headers)
            repos = resp.json()
            res = [{"name": r["name"], "full_name": r["full_name"], "url": r["html_url"]} for r in repos]
            return json.dumps(res, indent=2)

    @mcp.tool()
    async def github_create_repo(name: str, description: str = None, private: bool = False) -> str:
        """Criar um novo repositório no seu GitHub."""
        headers = get_headers()
        if not headers: return "GitHub não configurado."
        
        async with httpx.AsyncClient() as client:
            resp = await client.post("https://api.github.com/user/repos", headers=headers, json={
                "name": name,
                "description": description,
                "private": private
            })
            data = resp.json()
            return f"Repositório criado com sucesso: {data.get('html_url')}"

    @mcp.tool()
    async def github_push_file(owner: str, repo: str, path: str, content: str, message: str, branch: str = "main") -> str:
        """Fazer o 'push' de um arquivo para o GitHub (cria ou atualiza)."""
        headers = get_headers()
        if not headers: return "GitHub não configurado."
        
        async with httpx.AsyncClient() as client:
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
            sha = None
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    sha = resp.json().get("sha")
            except: pass

            payload = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch
            }
            if sha: payload["sha"] = sha
            
            resp = await client.put(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers, json=payload)
            if resp.status_code in [200, 201]:
                return f"Arquivo {path} enviado com sucesso para {owner}/{repo}."
            return f"Erro ao enviar arquivo: {resp.text}"

    @mcp.tool()
    async def github_delete_repo(owner: str, repo: str) -> str:
        """Excluir um repositório no GitHub."""
        headers = get_headers()
        if not headers: return "GitHub não configurado."
        
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
            if resp.status_code == 204:
                return f"Repositório {owner}/{repo} excluído com sucesso."
            return f"Erro ao excluir repositório: {resp.text}"
