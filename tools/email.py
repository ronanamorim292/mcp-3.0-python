import httpx
import os
from mcp.server.fastmcp import FastMCP

def register_email_tools(mcp: FastMCP):
    api_key = os.getenv("RESEND_API_KEY")

    @mcp.tool()
    async def email_send(to: str, subject: str, html: str, from_email: str = "onboarding@resend.dev") -> str:
        """Envia um email profissional usando o Resend."""
        if not api_key: return "Resend não configurado."
        
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "from": from_email,
            "to": [to],
            "subject": subject,
            "html": html
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                return f"Erro ao enviar email: {resp.text}"
            data = resp.json()
            return f"Email enviado com sucesso! ID: {data.get('id')}"
