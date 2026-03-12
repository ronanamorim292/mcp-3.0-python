from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.query import Query
import os
import datetime
from mcp.server.fastmcp import FastMCP

def register_secrets_tools(mcp: FastMCP):
    endpoint = os.getenv("APPWRITE_ENDPOINT")
    project = os.getenv("APPWRITE_PROJECT")
    api_key = os.getenv("APPWRITE_API_KEY")
    db_id = os.getenv("APPWRITE_DATABASE_ID", "main")
    collection_id = "secrets"

    def get_databases():
        if not endpoint or not project or not api_key: return None
        client = Client()
        client.set_endpoint(endpoint)
        client.set_project(project)
        client.set_key(api_key)
        return Databases(client)

    @mcp.tool()
    async def secrets_save(service: str, key: str, description: str = None) -> str:
        """Salva com segurança uma chave de API ou segredo de um serviço."""
        databases = get_databases()
        if not databases: return "Appwrite não configurado."
        
        try:
            existing = databases.list_documents(db_id, collection_id, [Query.equal("service", service)])
            if existing.get("total", 0) > 0:
                doc_id = existing["documents"][0]["$id"]
                databases.update_document(db_id, collection_id, doc_id, {
                    "key": key,
                    "description": description,
                    "updated_at": datetime.datetime.utcnow().isoformat()
                })
                return f"Chave do serviço '{service}' atualizada no cofre."
            
            databases.create_document(db_id, collection_id, ID.unique(), {
                "service": service,
                "key": key,
                "description": description,
                "updated_at": datetime.datetime.utcnow().isoformat()
            })
            return f"Novo segredo salvo para: {service}"
        except Exception as e:
            return f"Erro ao salvar segredo: {str(e)}"

    @mcp.tool()
    async def secrets_get(service: str) -> str:
        """Recupera a chave de API de um serviço específico do seu cofre."""
        databases = get_databases()
        if not databases: return "Appwrite não configurado."
        
        try:
            result = databases.list_documents(db_id, collection_id, [Query.equal("service", service)])
            if result.get("total", 0) == 0: return f"Nenhuma chave encontrada para o serviço '{service}'."
            secret = result["documents"][0]
            return f"🔑 Resgatada! Chave de {service}: {secret['key']}"
        except Exception as e:
            return f"Erro ao recuperar segredo: {str(e)}"

    @mcp.tool()
    async def secrets_list() -> str:
        """Lista todos os serviços que possuem chaves salvas (sem mostrar as chaves)."""
        databases = get_databases()
        if not databases: return "Appwrite não configurado."
        
        try:
            result = databases.list_documents(db_id, collection_id)
            if result.get("total", 0) == 0: return "Seu cofre está vazio."
            
            l = [f"- {d['service']} ({d.get('description', 'Sem descrição')})" for d in result["documents"]]
            return "Serviços no cofre:\n" + "\n".join(l)
        except Exception as e:
            return f"Erro ao listar cofre: {str(e)}"
