from voz import gravar, transcrever

gravar(5, "teste.wav")
print("Você disse:", transcrever("teste.wav"))