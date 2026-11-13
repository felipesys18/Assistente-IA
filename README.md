# Devmais

Assistente de IA por voz, estilo "Jarvis", feito para estudo e programação.
Projeto de aprendizado em Python, **100% gratuito**.

```
voz → faster-whisper → LLM (Gemini ou Ollama) → Piper → voz
```

Você fala (no terminal do notebook ou pelo navegador do celular), o Devmais
transcreve, pensa e responde em voz alta, lembrando da conversa.

## Funcionalidades

- Conversa por texto no terminal, com memória da conversa
- Entrada por voz (faster-whisper, roda local na CPU)
- Resposta em voz (Piper, roda local na CPU)
- Provedor de LLM trocável por uma linha no `.env` (Gemini ou Ollama)
- Retry automático (backoff exponencial) para erros 429 e 503
- Servidor FastAPI com página web (texto, microfone e áudio de volta)
- Acesso pelo celular via Tailscale, sem abrir portas no roteador

## Stack

| Peça | Para quê |
|---|---|
| Python | Linguagem |
| Gemini API (nível gratuito) | LLM padrão |
| Ollama (opcional) | LLM local, plano B |
| faster-whisper | Voz → texto |
| Piper | Texto → voz |
| FastAPI + Uvicorn | Servidor web |
| Tailscale (plano gratuito) | Rede privada notebook ↔ celular |

## Requisitos

- Windows (testado), Python 3.12 ou superior
- Microfone e caixas de som (ou fone)
- Chave gratuita do Google AI Studio: https://aistudio.google.com/apikey

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do exemplo e coloque sua chave:

```powershell
Copy-Item .env.example .env
```

Edite o `.env` (nunca envie esse arquivo ao GitHub):

```
GEMINI_API_KEY=cole_sua_chave_aqui
GEMINI_MODEL=nome_do_modelo
LLM_PROVEDOR=gemini
```

> Os nomes dos modelos e os limites do nível gratuito mudam com frequência.
> Confira o modelo disponível no AI Studio (menu "Limite de taxa") e
> ajuste o `GEMINI_MODEL`.

Baixe uma voz do Piper em português do Brasil (a pasta `models/` não vai pro Git):

```powershell
python -m piper.download_voices pt_BR-jeff-medium --download-dir models
```

## Como rodar

### No terminal (voz, sem servidor)

```powershell
python devmais.py
```

Fale normalmente. Comandos de voz: **"limpar memória"** e **"encerrar"**.

### Chat por texto

```powershell
python chat_texto.py
```

### Servidor web + celular

1. Suba o servidor, **somente local**:

```powershell
uvicorn servidor:app --host 127.0.0.1 --port 8000
```

2. Abra `http://127.0.0.1:8000/` no navegador do notebook.

3. Para usar no celular, instale o Tailscale nos dois aparelhos (mesma conta),
   ative o HTTPS no painel do Tailscale e rode:

```powershell
tailscale serve --bg 8000
tailscale serve status
```

4. Abra no celular o endereço `https://...ts.net` mostrado pelo `status`.
   O navegador só libera o microfone em HTTPS, por isso o `tailscale serve`.

## Estrutura do projeto

```
llm.py              função única perguntar() com provedor trocável e retry
voz.py              gravar(), transcrever(), falar() e sintetizar_wav()
jarvis.py           assistente por voz no terminal
chat_texto.py       chat por texto no terminal
chat_voz_entrada.py voz → texto → LLM com memória (versão simples)
servidor.py         API FastAPI (/chat, /voz, /limpar, /ping)
static/index.html   página web (texto, microfone, áudio de resposta)
.env.example        modelo do .env (sem segredos)
```

## Segurança

- Chaves ficam só no `.env`, que está no `.gitignore`
- O servidor escuta apenas em `127.0.0.1`; quem expõe é o Tailscale
- Nenhuma porta é aberta no roteador
- No nível gratuito do Gemini, o Google pode usar os prompts para treino:
  **não envie dados sensíveis**
- Não compartilhe o notebook no Tailscale com outras pessoas: cada
  mensagem gasta a sua cota

## Roadmap

- [x] Etapa 1: ambiente e revisão de Python
- [x] Etapa 2: conversa com o LLM por texto
- [x] Etapa 3: memória da conversa
- [x] Etapa 4: gravar e transcrever voz
- [x] Etapa 5: responder em voz
- [x] Etapa 6: tudo junto no terminal
- [x] Etapa 7: acesso pelo celular
- [ ] Etapa 8: ferramentas (`abrir_painel`: código com destaque e fluxogramas)
- [ ] Etapa 9: modos de estudo (explicar, quiz, flashcards, resumo)
- [ ] Etapa 10: memória de longo prazo, palavra de ativação, tempo real

## Licenças

O Piper (`piper-tts`) é distribuído sob GPL-3.0, e cada voz tem licença própria.
Confira antes de distribuir o projeto.
