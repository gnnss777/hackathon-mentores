import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

chunks = json.load(open("api/chunks.json", encoding="utf-8"))

testes = [
    "onde cadastro minha equipe",
    "precisa de quantas pessoas no discord para formar time",
    "nao consigo ver minha equipe no criartime",
    "como escolher o desafio",
    "ate quando pode escolher o desafio",
    "como funciona a entrega 1",
    "tem limite de caracteres",
]

for pergunta in testes:
    q_words = set(re.sub(r'[^a-z0-9\s]', '', pergunta.lower()).split())
    found_duvidas = False
    for c in chunks:
        c_words = set(re.sub(r'[^a-z0-9\s]', '', c["texto"].lower()).split())
        overlap = len(q_words & c_words)
        if overlap > 0 and c["fonte"] == "duvidas-discord":
            found_duvidas = True
            break
    status = "ENCONTROU" if found_duvidas else "NAO encontrou"
    print(f"  [{status}] {pergunta}")
