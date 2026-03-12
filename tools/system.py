import os
from mcp.server.fastmcp import FastMCP

def register_system_tools(mcp: FastMCP):
    env_path = os.path.abspath(os.path.join(os.getcwd(), ".env"))

    @mcp.tool()
    async def system_env_get(key: str) -> str:
        """Obter o valor de uma variável de ambiente do arquivo .env."""
        if not os.path.exists(env_path): return ".env não encontrado"
        with open(env_path, "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    return line.split("=")[1].strip()
        return f"Chave {key} não encontrada."

    @mcp.tool()
    async def system_env_set(key: str, value: str) -> str:
        """Adicionar ou atualizar uma variável no arquivo .env."""
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        found = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"{key}={value}\n")
            
        with open(env_path, "w") as f:
            f.writelines(new_lines)
        return f"Variável {key} salva com sucesso."

    @mcp.tool()
    async def system_get_logs(lines: int = 50) -> str:
        """Obter os logs recentes do servidor MCP."""
        return "Logs estão sendo emitidos via stderr. Verifique o terminal ou gerenciador de processos."
