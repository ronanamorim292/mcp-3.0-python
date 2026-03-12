import httpx
import json
import os
from mcp.server.fastmcp import FastMCP
import urllib.parse

def register_easypanel_tools(mcp: FastMCP):
    url = os.getenv("EASYPANEL_URL")
    api_key = os.getenv("EASYPANEL_API_KEY")

    def get_client():
        if not url or not api_key:
            return None
        return httpx.AsyncClient(
            base_url=f"{url}/api/trpc",
            headers={"Authorization": f"Bearer {api_key}"}
        )

    @mcp.tool()
    async def easypanel_list_projects() -> str:
        """Listar projetos do EasyPanel."""
        client = get_client()
        if not client: return "EasyPanel não configurado."
        
        input_data = json.dumps({"0": {"json": None}})
        async with client:
            resp = await client.get(f"/projects.listProjects?batch=1&input={urllib.parse.quote(input_data)}")
            data = resp.json()
            projects = data[0].get("result", {}).get("data", {}).get("json") or data
            return json.dumps(projects, indent=2)

    @mcp.tool()
    async def easypanel_list_services(project_name: str) -> str:
        """Listar serviços de um projeto específico."""
        client = get_client()
        if not client: return "EasyPanel não configurado."
        
        input_data = json.dumps({"0": {"json": {"projectName": project_name}}})
        async with client:
            resp = await client.get(f"/projects.listProjectsAndServices?batch=1&input={urllib.parse.quote(input_data)}")
            data = resp.json()
            res = data[0].get("result", {}).get("data", {}).get("json") or data
            return json.dumps(res, indent=2)

    @mcp.tool()
    async def easypanel_deploy_service(project_name: str, service_name: str) -> str:
        """Disparar deploy de um serviço."""
        client = get_client()
        if not client: return "EasyPanel não configurado."
        
        async with client:
            await client.post("/services.deployService", json={"projectName": project_name, "serviceName": service_name})
            return f"Deploy iniciado para {service_name}"
