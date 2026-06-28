import json, re, requests, sys

video_id = sys.argv[1] if len(sys.argv) > 1 else "C8ZYcevVWfc"

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'pt-BR'})
s.get('https://www.youtube.com/', timeout=10)
r = s.get(f'https://www.youtube.com/watch?v={video_id}', timeout=15)
html = r.text
print(f'HTML len: {len(html)}')

key = 'ytInitialPlayerResponse'
start_marker = f'var {key} = '
pos = html.find(start_marker)
print(f'Found at pos: {pos}')
if pos >= 0:
    pos += len(start_marker)
    depth = 0
    in_string = False
    escape = False
    for i in range(pos, len(html)):
        c = html[i]
        if escape:
            escape = False
            continue
        if c == '\\' and in_string:
            escape = True
            continue
        if c == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end_pos = i + 1
                print(f'End at pos: {end_pos}')
                json_str = html[pos:end_pos]
                data = json.loads(json_str)
                vd = data.get('videoDetails', {})
                print(f"Title: {vd.get('title', '')[:80]}")
                print(f"Duration (lengthSeconds): {vd.get('lengthSeconds')}")
                print(f"Duration (lengthSeconds) type: {type(vd.get('lengthSeconds'))}")
                break
else:
    print("NOT FOUND - checking partial match...")
    if 'ytInitialPlayerResponse' in html:
        print("  String exists but var pattern not found")
        idx = html.find('ytInitialPlayerResponse')
        print(f"  Context: ...{html[idx-20:idx+80]}...")
