from voz import gravar_ate_silencio, transcrever

if gravar_ate_silencio("teste.wav"):
    print("Você disse: ", transcrever("teste.wav"))
else:
    print("Ninguém falou.")