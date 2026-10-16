from llm import perguntar

def main() -> None:
    print("Devmais no ar. Digite 'sair' pra encerrar.\n")
    while True:
        entrada = input("Digite algo: ").strip()
        if not entrada:
            continue #enter vazio: volta pro começo do loop
        if entrada.lower() in ("sair", "exit"):
            print("Até mais!")
            break
        try:
            print(f"Devmais: {perguntar(entrada)}\n")
        except Exception as e: #pega qualquer erro pro loop não caor
            print(f"[erro] {type(e).__name__}: {e}\n")

if __name__ == "__main__":
    main()