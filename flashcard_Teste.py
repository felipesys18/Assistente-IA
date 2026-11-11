from flashcard import adicionar, pendentes

print(adicionar("Pergunta difícil", "...", 3))   # True
print(adicionar("Pergunta fácil", "...", 1))     # True
print(adicionar("Pergunta fácil", "...", 1))     # False (duplicado)
print([c["frente"] for c in pendentes()])        # fácil antes da difícil