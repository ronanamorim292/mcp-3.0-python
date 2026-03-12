import httpx
import os
import json
import time
from mcp.server.fastmcp import FastMCP

def register_mp_tools(mcp: FastMCP):
    token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

    @mcp.tool()
    async def mp_create_pix_payment(amount: float, description: str, email: str, first_name: str = "Cliente", last_name: str = "MCP") -> str:
        """Gera um pagamento via PIX no Mercado Pago."""
        if not token: return "Mercado Pago não configurado."
        
        url = "https://api.mercadopago.com/v1/payments"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Idempotency-Key": str(int(time.time() * 1000))
        }
        payload = {
            "transaction_amount": amount,
            "description": description,
            "payment_method_id": "pix",
            "payer": {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            }
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            data = resp.json()
            if resp.status_code != 201:
                return f"Erro ao criar pagamento: {resp.text}"
            
            qi = data.get("point_of_interaction", {}).get("transaction_data", {})
            return f"Pagamento PIX criado!\nID: {data['id']}\nStatus: {data['status']}\n\nCódigo Copia e Cola:\n{qi.get('qr_code')}\n\nLink do QR Code:\n{qi.get('ticket_url')}"

    @mcp.tool()
    async def mp_get_payment_status(payment_id: str) -> str:
        """Verifica o status de um pagamento pelo ID."""
        if not token: return "Mercado Pago não configurado."
        url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return f"Erro ao buscar pagamento: {resp.text}"
            data = resp.json()
            return f"Status do Pagamento {payment_id}: {data['status']} ({data.get('status_detail')})"
