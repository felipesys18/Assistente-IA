import base64
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from llm import perguntar
from voz import sintetizar_wav, transcrever

app = FastAPI( ) #cria a api que recebe e responde às requisições 

historico: list[dict] = [ ] #armazena nossas mensagens da conversa em uma lista compartilhada pelo servidor

class Mensagem(BaseModel):
    """Formato esperado do corpo de pedido: {"texto": "..."}"""
    texto: str

@app.get("/ping")
def ping():
    return {"ok": True}

@app.post("/chat")
def chat(msg: Mensagem):
    historico.append({"role": "user", "content": msg.texto})
    try:
        resposta = perguntar(historico[-20:])
    except Exception as e:
        historico.pop( ) #remover as perguntas que não tiverem resposta
        return {"erro": f"{type(e) .__name__}: {e}"}
    historico.append({"role": "assistant", "content": resposta})
    audio = base64.b64encode(sintetizar_wav(resposta)).decode()
    return {"resposta": resposta, "audio": audio}

@app.post("/voz")
async def voz(audio: UploadFile = File(...)):
    #salvar o audio recebido em um arquivo temporário (mantendo a extensão)
    sufixo = Path(audio.filename or "fala.webm").suffix or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=sufixo) as tmp:
        tmp.write(await audio.read())
        caminho = tmp.name

    try:
        texto = transcrever(caminho) #whisper: audio -> texto
    except Exception as e:
        return {"erro": f"Falha ao transcrever: {type(e).__name__}: {e}"}
    finally:
        Path(caminho).unlink(missing_ok=True) #apaga o arquivo temporário

    if not texto:
        return {"erro": "Não entendi nada. Tente de novo."}

    #Mesma lógica do /chat
    historico.append({"role": "user", "content": texto})
    try:
        resposta = perguntar(historico[-20:])
    except Exception as e:
        historico.pop()
        return {"erro": f"{type(e).__name__}: {e}"}
    historico.append({"role": "assistant", "content": resposta})
    audio = base64.b64encode(sintetizar_wav(resposta)).decode()
    return {"texto": texto, "resposta": resposta, "audio": audio}

@app.post("/limpar")
def limpar():
    historico.clear()
    return {"ok": True}

@app.get("/")
def pagina_inicial():
    return FileResponse("static/index.html")

#arquivo extras(js, css, imagens) ficam acessíveis em /static/
app.mount("/static", StaticFiles(directory="static"), name="static")