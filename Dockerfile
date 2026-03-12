FROM python:3.12-slim

# Evitar arquivos .pyc e garantir logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante da aplicação
COPY . .

# Expor a porta 8000 para o SSE
EXPOSE 8000

# Healthcheck para garantir que o serviço está rodando
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/ || exit 1

# Comando para rodar o servidor usando o entrypoint compatible com o MCP SSE
# Adicionado --forwarded-allow-ips='*' para resolver de vez problemas de Host/Proxy
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000", "--http", "h11", "--proxy-headers", "--forwarded-allow-ips='*'"]
