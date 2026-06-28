import requests, re, json

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36', 'Accept-Language': 'pt-BR,pt;q=0.9'})
s.get('https://www.youtube.com/', timeout=10)

for vid in ['dQw4w9WgXcQ', 'dzJ5B4fZYMg', 'C8ZYcevVWfc']:
    r = s.get(f'https://www.youtube.com/watch?v={vid}', timeout=15)
    m = re.search(r'var\s+ytInitialPlayerResponse\s*=\s*{', r.text)
    if not m:
        print(f'{vid}: no ytIPR')
        continue
    pos = m.end() - 1
    depth = 0; in_str = False; esc = False; end = 0
    html = r.text
    for i in range(pos, len(html)):
        c = html[i]
        if esc: esc = False; continue
        if c == '\\' and in_str: esc = True; continue
        if c == '"': in_str = not in_str; continue
        if in_str: continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: end = i + 1; break
    data = json.loads(html[pos:end])
    ps = data.get('playabilityStatus', {})
    vd = data.get('videoDetails', {})
    print(f'{vid}: playability={ps.get("status")} videoDetails={list(vd.keys())[:5] if vd else "NONE"} dur={vd.get("lengthSeconds")}')
