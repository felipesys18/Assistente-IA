import html #html.escape: impede que o texto vire código HTML
import webbrowser #serve para abrir o navegador do notebook/computador

from pathlib import Path #caminhos de arquivos
from uuid import uuid4 #gera nomes únicos (evitando sobrescrever painéis)

PASTA = Path(__file__).parent / "paineis" #pasta onde os painéis serão salvos
TIPOS_PERMITIDOS = ("codigo", "fluxograma") #lista curta de ações que são permitidas

# {titulo} e {conteudo} serão preenchidos depois com .format()
# {{ }} em dobro: porque o .format() usa { } e o CSS/JS também
MODELO_CODIGO = """<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><title>{titulo}</title>
<link rel="stylesheet"
 href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>body{{background:#111;color:#eee;font-family:sans-serif;padding:1rem}}</style>
</head><body><h2>{titulo}</h2>
<pre><code>{conteudo}</code></pre>
<script>hljs.highlightAll();</script></body></html>"""

MODELO_FLUXOGRAMA = """<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><title>{titulo}</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<style>body{{background:#fff;font-family:sans-serif;padding:1rem}}</style>
</head><body><h2>{titulo}</h2>
<pre class="mermaid">{conteudo}</pre>
<script>mermaid.initialize({{startOnLoad:true}});</script></body></html>"""

def abrir_painel(tipo: str, titulo: str, conteudo: str) -> str:
    """Abre uma aba no navegador do notebook ou do computador para mostrar algo na tela
    
    Use quando o usuário pedir um exemplo de código ou um fluxograma.
    tipo: "codigo" (codigo com destaque e muito bem elaborado) ou "fluxograma" (diagrama Mermaid e bem explicado).
    titulo: título curto da página.
    conteudo: o código ou o diagrama Mermaid completo.
    """

    if tipo not in TIPOS_PERMITIDOS:
        return f"Tipo Inválido. Use um destes: {TIPOS_PERMITIDOS}"

        #colocamos um if/else para escolher o modelo
    modelo = MODELO_CODIGO if tipo == "codigo" else MODELO_FLUXOGRAMA
    pagina = modelo.format(
            #nessa parte colocamos para preencher os cantos de titulo e de conteudo.
        titulo=html.escape(titulo), #o texto não virar script
        conteudo=html.escape(conteudo),
        )

    PASTA.mkdir(exist_ok=True)  #cria painéis se não existir
    arquivo = PASTA / f"{uuid4().hex}.html" #nome único para cada painel
    arquivo.write_text(pagina, encoding="utf-8")
    webbrowser.open(arquivo.as_uri()) #abre nosso navegador do notebook
    return "Painel aberto na tela"