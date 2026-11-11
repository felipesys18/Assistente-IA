import json
from datetime import date, timedelta
from pathlib import Path

ARQUIVO = Path(__file__).parent / "cartoes.json" #serve para guarda os flashs cards já criados sem usar banco de dados
INTERVALOS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16} #caixa dias até revisar

def carregar( ) -> list[dict]:
    if not ARQUIVO.exists(): #verificação leve
        return [] #caixa vazia
    texto = ARQUIVO.read_text(encoding="utf-8") #ler o arquivo como texto
    return json.loads(texto)#converter texto JSON em objeto python

def salvar(cartoes: list[dict]) -> None:
    texto = json.dumps(cartoes, ensure_ascii=False, indent=2) #ensure_ascii=False serve para acentos legiveis, sem ele fica toda uma bagunça no arquivo
    ARQUIVO.write_text(texto, encoding="utf-8")

def adicionar(frente: str, verso: str, dificuldade: int = 2) -> bool:
    cartoes = carregar() #abre a pasta 

    if any(c["frente"] == frente for c in cartoes):
        return False #já exite não duplica

    cartoes.append({ #coloca a ficha nova dentro da pasta
        "frente": frente,
        "verso": verso,
        "caixa": 1, #nivel de aprendizado
        "proxima": date.today().isoformat(), #quando revisar: hoje
        "dificuldade": dificuldade,
    })
    salvar(cartoes) #fecha a pasta
    return True #criou de verade

def pendentes() -> list[dict]:
    cartoes = carregar()
    hoje = date.today().isoformat()       # texto "2026-11-11"
    # <= deixa entrar os atrasados e os de hoje; os de amanhã ficam de fora
    lista = [c for c in cartoes if c["proxima"] <= hoje]
    return sorted(lista, key=lambda c: c.get("dificuldade", 2))

def responder(frente: str, acertou: bool) -> str:
    cartoes = carregar()
    for c in cartoes:
        if c["frente"] == frente:   #acha o cartão pela pergunta
            if acertou:
                c["caixa"] = min(5, c["caixa"] + 1)   #sobe uma caixa, máximo 5
            else:
                c["caixa"] = 1    #errou: volta pro começo
            dias = INTERVALOS[c["caixa"]]
            c["proxima"] = (date.today() + timedelta(days=dias)).isoformat()
            salvar(cartoes)
            return f"Caixa {c['caixa']}, volta em {dias} dia(s)."
    return "Cartão não encontrado."