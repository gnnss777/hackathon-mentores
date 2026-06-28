import urllib.request, re, json

video_id = 'dQw4w9WgXcQ'
req = urllib.request.Request(
    f'https://www.youtube.com/watch?v={video_id}',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)
try:
    html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='replace')
    m = re.search(r'approxDurationMs["\']?\s*:\s*["\']?(\d+)["\']?', html)
    print('Found:', m.group(1) if m else 'NOT FOUND')
    if not m:
        ms = re.findall(r'approxDurationMs["\']?\s*:\s*["\']?(\d+)["\']?', html)
        print('All matches:', ms[:10])
        print('HTML length:', len(html))
        # look in a smaller portion
        snippet = html[html.find('duration'):html.find('duration')+200] if 'duration' in html else 'NO DURATION KEY'
        print('Snippet:', snippet[:300])
except Exception as e:
    print('Error:', e)
