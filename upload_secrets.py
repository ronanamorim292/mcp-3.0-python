import os
import subprocess
from dotenv import dotenv_values

def upload_secrets():
    # Carrega as variáveis do arquivo .env
    env_vars = dotenv_values(".env")
    
    if not env_vars:
        print("Erro: Arquivo .env não encontrado ou vazio.")
        return

    print(f"Encontradas {len(env_vars)} variáveis no .env. Iniciando upload para o Cloudflare...")

    for key, value in env_vars.items():
        if not value:
            print(f"Pulando {key} (valor vazio)")
            continue
            
        print(f"Enviando {key}...")
        try:
            # Executa o comando wrangler secret put
            # Usamos echo para passar o valor via stdin para evitar que ele apareça nos logs do terminal
            process = subprocess.Popen(
                ["wrangler", "secret", "put", key],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=value)
            
            if process.returncode == 0:
                print(f"✅ {key} enviado com sucesso.")
            else:
                print(f"❌ Erro ao enviar {key}: {stderr}")
        except Exception as e:
            print(f"❌ Falha crítica ao processar {key}: {str(e)}")

    print("\nConcluído! Agora você pode rodar 'wrangler deploy'.")

if __name__ == "__main__":
    upload_secrets()
