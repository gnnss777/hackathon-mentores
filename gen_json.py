import json, re

with open('mentores.min.json', 'r', encoding='utf-8') as f:
    text = f.read()

# escape for JS single-quoted string
text = text.replace('\\', '\\\\')
text = text.replace("'", "\\'")
text = text.replace('\n', '\\n')
text = text.replace('\r', '')

with open('mentores_js.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print(len(text))
