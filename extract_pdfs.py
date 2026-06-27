from PyPDF2 import PdfReader
from pathlib import Path
import os

pdfs = {
    "briefing": "haCARthon - Briefing dos desafios - versão 2.pdf",
    "guia": "haCARthon - Guia do Participante.pdf"
}

output_dir = Path("C:/OPENCODE/HACKATON/extraido")
output_dir.mkdir(exist_ok=True)

for nome, arquivo in pdfs.items():
    caminho = Path("C:/OPENCODE/HACKATON") / arquivo
    reader = PdfReader(str(caminho))
    texto = ""
    for page in reader.pages:
        texto += page.extract_text() + "\n"
    saida = output_dir / f"{nome}.txt"
    saida.write_text(texto, encoding="utf-8")
    print(f"Extraído: {saida} ({len(texto)} caracteres)")
