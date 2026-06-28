from PyPDF2 import PdfReader
from pathlib import Path

PASTA_HACK = Path("C:/OPENCODE/HACKATON")
PASTA_OUT = PASTA_HACK / "extraido"
PASTA_OUT.mkdir(exist_ok=True)

pdfs = {
    "briefing": "haCARthon - Briefing dos desafios - versão 2.pdf",
    "guia": "haCARthon - Guia do Participante.pdf",
    "edital": "Edital haCARthon - Assinado - SEI_0993344_Edital_158.pdf",
    "acesso_cadastro": "Acesso ao Módulo de Cadastro Pré- Preenchido.pdf",
    "panic_lobster": "Panic Lobster.pdf",
}

for nome, arquivo in pdfs.items():
    caminho = PASTA_HACK / arquivo
    if not caminho.exists():
        print(f"PULANDO (não encontrado): {arquivo}")
        continue
    reader = PdfReader(str(caminho))
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    saida = PASTA_OUT / f"{nome}.txt"
    saida.write_text(texto, encoding="utf-8")
    print(f"OK: {saida} ({len(texto)} chars)")
