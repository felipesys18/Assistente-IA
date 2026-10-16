import os, time 
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

SYSTEM_PROMPT = (
    "Você é o Devmais, um assistente de estudos e programação. "
    "Responda sempre em português do Brasil, de forma curta e direta, "
    "com explicações mais elaboradas quando necessário. "
    "Não use markdown, emojis ou listas longas."
)

MAX_TENTATIVAS = 5
CODIGOS_TEMPORARIOS = (429, 503) #Limite estourado / servidor sobrecarregado
_cliente_gemini = None

def _gemini(prompt: str) -> str:
    global _cliente_gemini
    if _cliente_gemini is None:
        chave = os.getenv("GEMINI_API_KEY")
        if not chave:
            raise RuntimeError ("GEMINI_API_KEY não encontrada no .env")
        _cliente_gemini = genai.Client(api_key = chave)

    resposta = _cliente_gemini.models.generate_content(
        model=os.environ["GEMINI_MODEL"],
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    return resposta.text or "" #basicamente o texto pode vim None se a resposta for bloqueada

def _ollama(prompt: str) -> str:
    #ollama rroda o servidor local com na porta 11434

    r = requests.post(
        "http://localhost:11434/api/generate", 
        json={
            "model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            "system": SYSTEM_PROMPT,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120, #modelo local em cpu que pode demorar
    )
    r.raise_for_status()
    return r.json()["response"]

#local para os provedores, para adicionar outro só incluir aqui dentro

PROVEDORES = {"gemini": _gemini, "ollama": _ollama}

def perguntar(prompt: str) -> str:
    """Única porta de entrado pro LLM. O resto do projeto só chama isso."""
    funcao = PROVEDORES[os.getenv("LLM_PROVEDOR", "gemini")]

    for tentativa in range (MAX_TENTATIVAS):
        try:
            return funcao(prompt)
        except errors.APIError as e:
            ultima = tentativa == MAX_TENTATIVAS - 1
            if e.code not in CODIGOS_TEMPORARIOS or ultima:
                raise #da um erro de verdade (chave ou modelo): não adiante repetir
            espera = 2 ** (tentativa + 1)
            print(f"[erro {e.code}, tentando de novo em {espera}s...]")
            time.sleep(espera)
    return ""