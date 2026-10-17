from llm import perguntar


def main() -> None:
    print("Devmais no ar. Digite 'sair' pra encerrar ou 'limpar' pra zerar a memória.\n")

    historico: list[dict] = []  # a memória: começa vazia e só cresce
    LIMITE = 20  # máximo de mensagens reenviadas (controle de custo)

    while True:
        entrada = input("Você: ").strip()  # strip tira espaços das pontas

        if not entrada:
            continue  # Enter vazio: volta pro começo do loop

        if entrada.lower() in ("sair", "exit"):
            print("Até mais!")
            break  # quebra o while e termina o programa

        if entrada.lower() == "limpar":
            historico.clear()  # esvazia a lista
            print("[memória apagada]\n")
            continue

        # 1) anota a sua fala
        historico.append({"role": "user", "content": entrada})

        try:
            # 2) manda só as últimas LIMITE mensagens
            resposta = perguntar(historico[-LIMITE:])
        except Exception as e:  # pega qualquer erro pro loop não cair
            print(f"[erro] {type(e).__name__}: {e}\n")
            historico.pop()  # remove a pergunta que ficou sem resposta
            continue

        # 3) anota a resposta do Devmais e mostra na tela
        historico.append({"role": "assistant", "content": resposta})
        print(f"Devmais: {resposta}\n")


if __name__ == "__main__":
    main()