from llm import perguntar
from voz import falar, gravar, transcrever
import traceback

SEGUNDOS = 10 #ajuste de tempo de gravação em segundos dps configuro para ser até quando a pessoa parar de falar.

def main() -> None:
    historico: list[dict] = [] #memória da conversa
    print("[Enter = falar] | digite 'sair' + Enter para encerrar\n")

    while True:
        #enter vazio = começa a gravar e sair encerra
        if input("[Enter para falar] ").strip().lower() == "sair":
            print("Até mais!")
            break

        gravar(SEGUNDOS, "fala.wav") #minha fala vira arquivo .wav
        texto = transcrever("fala.wav") #.wav vira texto usando o whisper

        if not texto: #silencio ou ruído nada acontence ou é reconhecido
            print("[Não entendi nada, tente de novo]\n")
            continue
        print(f"Você: {texto}")

        historico.append({"role": "user", "content": texto})
        try:
            resposta = perguntar(historico[-20:])
        except Exception as e:
            print(f"[erro {type(e).__name__}: {e}\n]")
            traceback.print_exc() #mostra a parte onde quebrou(exata)
            historico.pop()
            continue

        #devolve a resposta
        historico.append({"role": "user", "content": resposta})
        print(f"Devmais: {resposta}\n") 
        falar(resposta)

if __name__ == "__main__":
    main()