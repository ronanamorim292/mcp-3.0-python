FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para algumas ferramentas se houver
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expor a porta 8000 para o SSE
EXPOSE 8000

# Comando para rodar o servidor usando o entrypoint compatible com o MCP SSE
# Usamos o api/index.py pois ele já tem o Starlette configurado para SSE
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000", "--http", "h11"]
