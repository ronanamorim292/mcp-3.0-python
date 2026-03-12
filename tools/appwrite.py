from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.storage import Storage
from appwrite.services.users import Users
from appwrite.id import ID
from appwrite.query import Query
import os
import json
from mcp.server.fastmcp import FastMCP

def register_appwrite_tools(mcp: FastMCP):
    endpoint = os.getenv("APPWRITE_ENDPOINT")
    project = os.getenv("APPWRITE_PROJECT")
    api_key = os.getenv("APPWRITE_API_KEY")

    def get_services():
        if not endpoint or not project or not api_key:
            return None, None, None
        client = Client()
        client.set_endpoint(endpoint)
        client.set_project(project)
        client.set_key(api_key)
        return Databases(client), Storage(client), Users(client)

    @mcp.tool()
    async def appwrite_list_databases() -> str:
        """Listar todos os bancos de dados do Appwrite."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        res = databases.list()
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_create_database(name: str, database_id: str = None, enabled: bool = True) -> str:
        """Criar um novo banco de dados no Appwrite."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        res = databases.create(database_id or ID.unique(), name, enabled)
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_list_collections(database_id: str) -> str:
        """Listar coleções de um banco de dados."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        res = databases.list_collections(database_id)
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_create_collection(database_id: str, name: str, collection_id: str = None, permissions: list = None, document_security: bool = False) -> str:
        """Criar uma nova coleção em um banco de dados."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        res = databases.create_collection(database_id, collection_id or ID.unique(), name, permissions, document_security)
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_create_string_attribute(database_id: str, collection_id: str, key: str, size: int, required: bool, default_value: str = None, array: bool = False) -> str:
        """Criar atributo de texto em uma coleção."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        databases.create_string_attribute(database_id, collection_id, key, size, required, default_value, array)
        return f"Atributo de texto '{key}' criado."

    @mcp.tool()
    async def appwrite_create_integer_attribute(database_id: str, collection_id: str, key: str, required: bool, min_val: int = None, max_val: int = None, default_value: int = None, array: bool = False) -> str:
        """Criar atributo de número inteiro."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        databases.create_integer_attribute(database_id, collection_id, key, required, min_val, max_val, default_value, array)
        return f"Atributo numérico '{key}' criado."

    @mcp.tool()
    async def appwrite_create_boolean_attribute(database_id: str, collection_id: str, key: str, required: bool, default_value: bool = None, array: bool = False) -> str:
        """Criar atributo booleano."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        databases.create_boolean_attribute(database_id, collection_id, key, required, default_value, array)
        return f"Atributo booleano '{key}' criado."

    @mcp.tool()
    async def appwrite_list_documents(database_id: str, collection_id: str, queries: list = None) -> str:
        """Listar documentos de uma coleção."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        res = databases.list_documents(database_id, collection_id, queries)
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_create_document(database_id: str, collection_id: str, data: dict, document_id: str = None) -> str:
        """Criar um novo documento em uma coleção."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        res = databases.create_document(database_id, collection_id, document_id or ID.unique(), data)
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_update_document(database_id: str, collection_id: str, document_id: str, data: dict) -> str:
        """Atualizar um documento existente."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        res = databases.update_document(database_id, collection_id, document_id, data)
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_delete_document(database_id: str, collection_id: str, document_id: str) -> str:
        """Deletar um documento."""
        databases, _, _ = get_services()
        if not databases: return "Appwrite não configurado."
        databases.delete_document(database_id, collection_id, document_id)
        return f"Documento {document_id} excluído."

    @mcp.tool()
    async def appwrite_list_buckets() -> str:
        """Listar buckets de armazenamento."""
        _, storage, _ = get_services()
        if not storage: return "Appwrite não configurado."
        res = storage.list_buckets()
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_list_files(bucket_id: str) -> str:
        """Listar arquivos de um bucket."""
        _, storage, _ = get_services()
        if not storage: return "Appwrite não configurado."
        res = storage.list_files(bucket_id)
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_delete_file(bucket_id: str, file_id: str) -> str:
        """Deletar um arquivo do Storage."""
        _, storage, _ = get_services()
        if not storage: return "Appwrite não configurado."
        storage.delete_file(bucket_id, file_id)
        return f"Arquivo {file_id} excluído."

    @mcp.tool()
    async def appwrite_list_users() -> str:
        """Listar usuários do projeto."""
        _, _, users = get_services()
        if not users: return "Appwrite não configurado."
        res = users.list()
        return json.dumps(res, indent=2)

    @mcp.tool()
    async def appwrite_create_user(email: str, password: str, name: str = None, user_id: str = None) -> str:
        """Criar um novo usuário no Appwrite."""
        _, _, users = get_services()
        if not users: return "Appwrite não configurado."
        res = users.create(user_id or ID.unique(), email, None, password, name)
        return json.dumps(res, indent=2)
