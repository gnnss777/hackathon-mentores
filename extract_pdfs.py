from pathlib import Path
import sys
sys.path.insert(0, str(Path.home() / "AppData/Local/Programs/Python/Python312/Lib/site-packages"))

try:
    from pypdf import PdfReader
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pypdf>=3.0.0"])
    from pypdf import PdfReader

PASTA = Path("C:/OPENCODE/HACKATON")
EXTRAIDO = PASTA / "extraido"

pdfs = [
    ("Acesso ao Módulo de Cadastro Pré- Preenchido.pdf", "acesso_cadastro"),
    ("haCARthon - Briefing dos desafios - versão 2.pdf", "briefing"),
    ("haCARthon - Guia do Participante.pdf", "guia"),
    ("Edital haCARthon - Assinado - SEI_0993344_Edital_158.pdf", "edital"),
]

for nome, stem in pdfs:
    caminho = PASTA / nome
    if not caminho.exists():
        print(f"  SKIP {nome} — não encontrado")
        continue
    reader = PdfReader(str(caminho))
    texto = []
    for pagina in reader.pages:
        t = pagina.extract_text()
        if t:
            texto.append(t)
    conteudo = "\n\n".join(texto)
    (EXTRAIDO / f"{stem}.txt").write_text(conteudo, encoding="utf-8")
    pag = len(reader.pages)
    print(f"  {stem}: {pag} páginas, {len(conteudo)} chars -> extraido/{stem}.txt")

print("\nPronto.")
