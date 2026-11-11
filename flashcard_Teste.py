from flashcard import adicionar, pendentes, responder

adicionar("O que é fotossíntese?", "Processo em que plantas transformam luz em energia.")
adicionar("Onde ocorre a fotossíntese?", "Nos cloroplastos.")

print("Pendentes:", len(pendentes()))  #esperado: 2
print(responder("O que é fotossíntese?", True))   #caixa 2, volta em 2 dias
print("Pendentes:", len(pendentes()))   #esperado: 1
print(responder("Onde ocorre a fotossíntese?", False))  #caixa 1, volta em 1 dia