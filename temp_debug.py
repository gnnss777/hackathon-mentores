import re, sys
sys.stdout.reconfigure(encoding="utf-8")
with open("extraido/guia.txt", encoding="utf-8") as f:
    texto = f.read()
print("Total:", len(texto), "chars")
paragrafos = re.split(r'\n\s*(?:\n\s*)+', texto)
print("Paragrafos (duplo \\n):", len(paragrafos))
paragrafos2 = [l for l in texto.split("\n") if l.strip()]
print("Linhas nao vazias:", len(paragrafos2))
for i, p in enumerate(paragrafos[:5]):
    print(f"  p{i}: {len(p)} chars -> {p[:80]}")
