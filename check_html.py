import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.index('var DATA = ') + len('var DATA = ')
end = html.index(';', start)
data_str = html[start:end]
data = json.loads(data_str)
print(f'JSON OK: {len(data)} records')
print(f'Has filterArea: {"filterArea" in html}')
print(f'Has data-g: {"data-g" in html}')
print(f'File size: {len(html)} bytes')
