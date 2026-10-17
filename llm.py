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

def _gemini(historico: list[dict]) -> str:
    global _cliente_gemini #avisa que eu irei atribuir essa variavel fora da função
    if _cliente_gemini is None:
        chave = os.getenv("GEMINI_API_KEY")
        if not chave:
            raise RuntimeError ("GEMINI_API_KEY não encontrada no .env")
        _cliente_gemini = genai.Client(api_key = chave)

    conteudo = [
        types.Content(
            role = "model" if m["role"] == "assistant" else "user",
            parts=[types.Part(text=m["content"])],
        )
        for m in historico
    ]

    resposta = _cliente_gemini.models.generate_content(
        model=os.environ["GEMINI_MODEL"],
        contents=conteudo,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
    )
    return resposta.text or "" #basicamente o texto pode vim None se a resposta for bloqueada

def _ollama(historico: list[dict]) -> str:
    mensagens = [{"role ": "system", "content": SYSTEM_PROMPT}] + historico #junta uma lista com outra (historico)

    #ollama rroda o servidor local com na porta 11434
    r = requests.post(
        "http://localhost:11434/api/generate", 
        json={
            "model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            "system": SYSTEM_PROMPT,
            "prompt": mensagens,
            "stream": False, #False = resposta inteira de uma vez 
        },
        timeout=120, #modelo local em cpu que pode demorar
    )
    r.raise_for_status() #erro HTTP vira exceção
    return r.json()["message"]["content"] #o /api/chat devolve neste caminho

#local para os provedores, para adicionar outro só incluir aqui dentro

PROVEDORES = {"gemini": _gemini, "ollama": _ollama}

#porta única onde o resto do projeto só conhece esta função
def perguntar(historico: list[dict]) -> str:
    """Recebe o cadderno completo e devolve a resposta do Devmais."""
    funcao = PROVEDORES[os.getenv("LLM_PROVEDOR", "gemini")] #escolhe o provedor

    for tentativa in range (MAX_TENTATIVAS): #0,1,2,3,4 tentativas
        try:
            return funcao(historico) #escolheu o fornecedor e devolve e sai
        except errors.APIError as e: #e = o "sinal" recebido (guarda o código)
            ultima = tentativa == MAX_TENTATIVAS - 1 # == compara; =guarda
            if e.code not in CODIGOS_TEMPORARIOS or ultima:
                raise #da um erro de verdade (chave ou modelo): não adiante repetir
            espera = 2 ** (tentativa + 1) #2s, 4s, 8, 16s e acaba
            print(f"[erro {e.code}, tentando de novo em {espera}s...]")
            time.sleep(espera)
    return ""