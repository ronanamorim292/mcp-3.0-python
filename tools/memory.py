from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.query import Query
import os
import datetime
from mcp.server.fastmcp import FastMCP

def register_memory_tools(mcp: FastMCP):
    endpoint = os.getenv("APPWRITE_ENDPOINT")
    project = os.getenv("APPWRITE_PROJECT")
    api_key = os.getenv("APPWRITE_API_KEY")
    db_id = os.getenv("APPWRITE_DATABASE_ID", "main")
    collection_id = "memory"

    def get_databases():
        if not endpoint or not project or not api_key: return None
        client = Client()
        client.set_endpoint(endpoint)
        client.set_project(project)
        client.set_key(api_key)
        return Databases(client)

    @mcp.tool()
    async def memory_save_fact(key: str, fact: str, category: str = "geral") -> str:
        """Salva uma informação importante sobre o usuário ou projeto para lembrar depois."""
        databases = get_databases()
        if not databases: return "Appwrite não configurado."
        
        try:
            existing = databases.list_documents(db_id, collection_id, [Query.equal("key", key)])
            if existing.get("total", 0) > 0:
                doc_id = existing["documents"][0]["$id"]
                databases.update_document(db_id, collection_id, doc_id, {
                    "fact": fact,
                    "category": category,
                    "updated_at": datetime.datetime.utcnow().isoformat()
                })
                return f"Memória '{key}' atualizada."
            
            databases.create_document(db_id, collection_id, ID.unique(), {
                "key": key,
                "fact": fact,
                "category": category,
                "updated_at": datetime.datetime.utcnow().isoformat()
            })
            return f"Nova memória salva: {key}"
        except Exception as e:
            return f"Erro ao salvar memória: {str(e)}"

    @mcp.tool()
    async def memory_recall(search: str = None, category: str = None) -> str:
        """Recupera memórias salvas baseadas em uma palavra-chave ou categoria."""
        databases = get_databases()
        if not databases: return "Appwrite não configurado."
        
        queries = []
        if search: queries.append(Query.contains("key", search))
        if category: queries.append(Query.equal("category", category))
        
        try:
            result = databases.list_documents(db_id, collection_id, queries)
            if result.get("total", 0) == 0: return "Nenhuma memória encontrada."
            
            mems = [f"[{d['category']}] {d['key']}: {d['fact']}" for d in result["documents"]]
            return "Memórias recuperadas:\n" + "\n".join(mems)
        except Exception as e:
            return f"Erro ao recuperar memória: {str(e)}"
