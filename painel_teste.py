from ferramentas import abrir_painel

print(abrir_painel("codigo", "loop for", "for i in range(3):\n print(i)"))
print(abrir_painel("fluxograma", "teste", "graph TD; A[Início] --> B[Fim]"))
print(abrir_painel("outra coisa", "x", "y")) #deve retornar só erro