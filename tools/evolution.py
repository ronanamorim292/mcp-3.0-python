import httpx
import os
import json
from mcp.server.fastmcp import FastMCP

def register_evolution_tools(mcp: FastMCP):
    def get_client():
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("EVOLUTION_API_URL")
        key = os.getenv("EVOLUTION_API_KEY")
        if not url or not key: return None
        return httpx.AsyncClient(
            base_url=url,
            headers={"apikey": key},
            verify=False
        )

    @mcp.tool()
    async def evolution_list_instances() -> str:
        """Listar todas as instâncias da Evolution API."""
        client = get_client()
        if not client: return "Evolution API não configurada."
        async with client:
            resp = await client.get("/instance/fetchInstances")
            return json.dumps(resp.json(), indent=2)

    @mcp.tool()
    async def evolution_create_instance(instance_name: str, token: str = None, number: str = None) -> str:
        """Criar uma nova instância no WhatsApp."""
        client = get_client()
        if not client: return "Evolution API não configurada."
        payload = {
            "instanceName": instance_name,
            "token": token,
            "number": number,
            "qrcode": True
        }
        async with client:
            resp = await client.post("/instance/create", json=payload)
            return json.dumps(resp.json(), indent=2)

    @mcp.tool()
    async def evolution_get_qrcode(instance_name: str) -> str:
        """Obter o QR Code de uma instância."""
        client = get_client()
        if not client: return "Evolution API não configurada."
        async with client:
            resp = await client.get(f"/instance/connect/{instance_name}")
            return json.dumps(resp.json(), indent=2)

    @mcp.tool()
    async def evolution_send_message(instance_name: str, number: str, text: str) -> str:
        """Enviar uma mensagem de texto via WhatsApp."""
        client = get_client()
        if not client: return "Evolution API não configurada."
        payload = {"number": number, "text": text}
        async with client:
            resp = await client.post(f"/message/sendText/{instance_name}", json=payload)
            return json.dumps(resp.json(), indent=2)

    @mcp.tool()
    async def evolution_delete_instance(instance_name: str) -> str:
        """Deletar uma instância da Evolution API."""
        client = get_client()
        if not client: return "Evolution API não configurada."
        async with client:
            resp = await client.delete(f"/instance/delete/{instance_name}")
            return json.dumps(resp.json(), indent=2)
