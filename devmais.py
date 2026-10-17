import traceback

from llm import perguntar
from voz import falar, gravar_ate_silencio, transcrever

LIMITE = 20 #mensagens reenviadas ao LLM

def normalizar(texto: str) -> str:
    """Minúsculo e sem pontuação, pra comparar comandos."""
    return texto.lower().strip(".,!?")

def main() -> None:
    historico: list[dict] = []
    print("Devmais no ar. Diga 'limpar memoria' ou 'encerrar'. Ctrl+C também sai\n")
    falar("Devmais online. Pode falar.")

    while True:
        #ouvir
        if not gravar_ate_silencio("falar.wav"):
            continue

        #transcrever
        texto = transcrever("falar.wav")
        if not texto:
            continue
        print(f"Você: {texto}")
        cmd = normalizar(texto)

        #comandos locais(não gastam chamada ao LLM)
        if cmd in ("encerrar", "sair", "tchau", "desligar"):
            falar("Até logo.")
            break
        if cmd in ("limpar memória", "limpar memoria", "esquecer tudo"):
            historico.clear()
            falar("Memória apagada.")
            continue

        #conversa normal
        historico.append({"role": "user", "content": texto})
        try:
            resposta = perguntar(historico[-LIMITE:])
        except Exception as e:
            print(f"[Erro] {type(e) .__name__}: {e}")
            traceback.print_exc()
            historico.pop()
            falar("Tive um problema ao pensar. Tente novamente porfavor.")
            continue

        historico.append({"role": "assistant", "content": resposta})
        print(f"Devmais: {resposta}\n")
        falar(resposta) #trava até terminar(não vai pegar a própria voz da ia)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt: #Crtl+C sai limpo, sem o traceback
        print("\nEncerrado.")