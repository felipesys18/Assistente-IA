import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

#O cliente vai pegar a chama que veio do .env
cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

resposta = cliente.models.generate_content(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    contents="Diga olá em uma frase curta com algo motivacional, em português"
)

print(resposta.text)