import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging

app = FastAPI(title="JARVIS AGENT")

# Configurar static e templates
static_path = os.path.join(os.path.dirname(__file__), "static")
templates_path = os.path.join(os.path.dirname(__file__), "templates")

app.mount("/static", StaticFiles(directory=static_path), name="static")
templates = Jinja2Templates(directory=templates_path)

@app.get("/", response_class=HTMLResponse)
async def jarvis_home(request: Request):
    return templates.TemplateResponse("jarvis.html", {"request": request})

@app.post("/ask")
async def ask_jarvis(request: Request):
    data = await request.json()
    query = data.get("query", "")
    # Aqui entrará a lógica de IA e Habilidades
    return {"response": f"Processando: {query}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
