import time
import numpy as np
import wave 
import sounddevice as sd

from piper import PiperVoice, SynthesisConfig
from pathlib import Path
from faster_whisper import WhisperModel

#gravar a voz e parar de gravar só quando eu parar de falar inves de falar em segundos
BLOCO = 0.1  #analisa o audio em pedaços de 0.1 segundos 
LIMIAR = 200  #volume minimo para contar como fala(pode ser ajustado futuramente caso necessario)
SILENCIO_FIM = 2.0 #segundos em silencio que pode considerar fim da fala
ESPERA_MAX = 8 #desiste de esperar se ngm falar em 8s
GRAVACAO_MAX = 120 #corta gravações muito longas

_CONFIG = SynthesisConfig(length_scale=1.1, noise_scale=0.4, noise_w_scale=0.6)

#caminho absoluto a partir deste arquivo: funciona de qualquer pasta
_CAMINHO_VOZ = Path(__file__).parent / "models" / "pt_BR-cadu-medium.onnx"

#carrega a voz uma vez
_piper = PiperVoice.load(str(_CAMINHO_VOZ))

#pode usar base ou small, base é mais rápido e small erra menos no portugues.
_model = WhisperModel("small", device="cpu", compute_type="int8")
TAXA = 16000 #amostras por segundo: o Whisper trabalha com 16kHz

def gravar(segundos: int, arquivo: str) -> None:
    """Grava o microfone padrão e salva com .wav."""
    print(f"[gravando {segundos}s... fale agora]")

    #sd.rec começa a gravar em segundo plano e devolve um array numpy
    #channels=1 = mono; dtype="int16" = formato padrão de .way;
    audio = sd.rec(int(segundos *TAXA), samplerate=TAXA, channels=1, dtype="int16")
    sd.wait()#trava até a gravação terminar
    print("[gravação terminada]")

    #o módulo wave já vem com o python: escreve o cabeçalho + os bytes
    with wave.open(arquivo, "wb") as w:
        w.setnchannels(1) #mono
        w.setsampwidth(2) #2 byte por amostra
        w.setframerate(TAXA)
        w.writeframes(audio.tobytes())

def gravar_ate_silencio(arquivo: str) -> bool:
    """Grava até você parar de falar. Devolve False se ninguém falou."""
    blocos = [] #todos os pedaços gravados
    falou = False #já ouvimos fala?
    silencio = 0.0 #há quanto tempo está quieto
    inicio = time.time()
    tam = int(TAXA * BLOCO)

    print("[Ouvindo...]")

    with sd.InputStream(samplerate=TAXA, channels=1, dtype="int16") as fluxo:
        while True: 
            dados, _= fluxo.read(tam)
            blocos.append(dados.copy())

            #volume medio do bloco
            volume = np.abs (dados).mean()

            if volume > LIMIAR:
                falou = True
                silencio = 0.0
            else:
                silencio += BLOCO
            
            agora = time.time() - inicio
            if falou and silencio >= SILENCIO_FIM:
                break  #falou e depois ficou calado(terminou de falar)
            if not falou and agora > ESPERA_MAX:
                return False #ninguém falou
            if agora > GRAVACAO_MAX:
                break

        audio = np.concatenate(blocos)
        with wave.open(arquivo, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(TAXA)
            w.writeframes(audio.tobytes())
        return True


def transcrever(arquivo: str) -> str:
    """Converte um .wav em texto."""

    # O método retorna os segmentos de texto e as informações do áudio.
    # Os segmentos são gerados sob demanda, então é necessário percorrê-los
    # para que a transcrição seja processada e o texto seja obtido.
    segmentos, _info = _model.transcribe(arquivo, language="pt", vad_filter=True, initial_prompt="Devmais")
    return " ".join(s.text.strip() for s in segmentos)

def falar (texto: str) -> None:
    """Sintetiza o texto com o Piper e toca nos alto-falantes"""
    pedacos = []
    taxa = 22050 #valor provisório o chunk traz a real taxa

    #systhesizs() é basicamente um gerador que devolve o aúdio em pedaços (AudioChunk)
    #um por frase, Só trabalha quando você percorrer el com o for
    for chunk in _piper.synthesize(texto, syn_config=_CONFIG):
        taxa = chunk.sample_rate
        pedacos.append(chunk.audio_int16_array) #numpy int16
    if not pedacos:
        return # texto vazio nao tem fala

    audio = np.concatenate(pedacos) #juntar todos os pedacos em um aúdio só
    sd.play(audio, int(taxa * 0.93)) #começar a tocar em segundo plano
    sd.wait() #espera terminar de falar