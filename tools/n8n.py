import httpx
import os
import json
from mcp.server.fastmcp import FastMCP

def register_n8n_tools(mcp: FastMCP):
    api_url = os.getenv("N8N_API_BASE_URL")
    api_key = os.getenv("N8N_API_KEY")
    webhook_url = os.getenv("N8N_WEBHOOK_URL")

    def get_client():
        if not api_url or not api_key: return None
        return httpx.AsyncClient(
            base_url=api_url,
            headers={"X-N8N-API-KEY": api_key}
        )

    @mcp.tool()
    async def n8n_list_workflows() -> str:
        """Listar todos os workflows no n8n."""
        client = get_client()
        if not client: return "n8n não configurado."
        async with client:
            resp = await client.get("/workflows")
            return json.dumps(resp.json(), indent=2)

    @mcp.tool()
    async def n8n_trigger_workflow(payload: dict = None, custom_webhook_url: str = None) -> str:
        """Disparar um workflow via webhook."""
        target = custom_webhook_url or webhook_url
        if not target: return "URL de webhook não configurada."
        async with httpx.AsyncClient() as client:
            resp = await client.post(target, json=payload or {})
            return json.dumps(resp.json(), indent=2)

    @mcp.tool()
    async def n8n_get_workflow(workflow_id: str) -> str:
        """Obter detalhes de um workflow específico."""
        client = get_client()
        if not client: return "n8n não configurado."
        async with client:
            resp = await client.get(f"/workflows/{workflow_id}")
            return json.dumps(resp.json(), indent=2)

    @mcp.tool()
    async def n8n_activate_workflow(workflow_id: str) -> str:
        """Ativar um workflow no n8n."""
        client = get_client()
        if not client: return "n8n não configurado."
        async with client:
            await client.post(f"/workflows/{workflow_id}/activate")
            return f"Workflow {workflow_id} ativado."

    @mcp.tool()
    async def n8n_deactivate_workflow(workflow_id: str) -> str:
        """Desativar um workflow no n8n."""
        client = get_client()
        if not client: return "n8n não configurado."
        async with client:
            await client.post(f"/workflows/{workflow_id}/deactivate")
            return f"Workflow {workflow_id} desativado."

    @mcp.tool()
    async def n8n_create_workflow(name: str, nodes: list, connections: dict, settings: dict = None) -> str:
        """Criar um novo workflow no n8n a partir de um JSON."""
        client = get_client()
        if not client: return "n8n não configurado."
        payload = {
            "name": name,
            "nodes": nodes,
            "connections": connections,
            "settings": settings or {"executionOrder": "v1"}
        }
        async with client:
            resp = await client.post("/workflows", json=payload)
            data = resp.json()
            return f"Workflow criado com sucesso! ID: {data.get('id')}"

    @mcp.tool()
    async def n8n_update_workflow(workflow_id: str, name: str = None, nodes: list = None, connections: dict = None, settings: dict = None) -> str:
        """Atualizar um workflow existente no n8n."""
        client = get_client()
        if not client: return "n8n não configurado."
        update_data = {}
        if name: update_data["name"] = name
        if nodes: update_data["nodes"] = nodes
        if connections: update_data["connections"] = connections
        if settings: update_data["settings"] = settings
        async with client:
            await client.put(f"/workflows/{workflow_id}", json=update_data)
            return f"Workflow {workflow_id} atualizado com sucesso."

    @mcp.tool()
    async def n8n_delete_workflow(workflow_id: str) -> str:
        """Excluir um workflow do n8n."""
        client = get_client()
        if not client: return "n8n não configurado."
        async with client:
            await client.delete(f"/workflows/{workflow_id}")
            return f"Workflow {workflow_id} excluído com sucesso."
