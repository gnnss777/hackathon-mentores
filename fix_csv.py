import csv, json

with open('haCARthon - Inscrições - Mentor.csv', 'r', encoding='latin-1', errors='replace') as f:
    reader = csv.DictReader(f)
    data = []
    for row in reader:
        clean = {}
        for k, v in row.items():
            if k:
                clean[k.strip()] = v.strip() if v else ''
        data.append(clean)

with open('mentores_clean.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'OK {len(data)} records')
