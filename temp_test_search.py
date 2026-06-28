import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

chunks = json.load(open("api/chunks.json", encoding="utf-8"))

pergunta = "Temos limite de caracteres nos textos da Entrega 1?"
q_words = set(re.sub(r'[^a-z0-9\s]', '', pergunta.lower()).split())
print("Query words:", q_words)
print()

scores = []
for i, c in enumerate(chunks):
    c_words = set(re.sub(r'[^a-z0-9\s]', '', c["texto"].lower()).split())
    overlap = len(q_words & c_words)
    if overlap > 0:
        scores.append((overlap, i, c["fonte"]))

scores.sort(key=lambda x: (-x[0], x[2]))
print("Top 15 resultados:")
for s in scores[:15]:
    fonte = s[2]
    texto = chunks[s[1]]["texto"][:100].replace("\n", " ")
    print(f"  overlap={s[0]:2d} fonte={fonte:25s} {texto}")
