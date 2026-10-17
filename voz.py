import wave 
import sounddevice as sd

from faster_whisper import WhisperModel

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

def transcrever(arquivo: str) -> str:
    """Converte um .wav em texto."""

    # O método retorna os segmentos de texto e as informações do áudio.
    # Os segmentos são gerados sob demanda, então é necessário percorrê-los
    # para que a transcrição seja processada e o texto seja obtido.
    segmentos, _info = _model.transcribe(arquivo, language="pt", vad_filter=True, initial_prompt="Devmais")
    return " ".join(s.text.strip() for s in segmentos)