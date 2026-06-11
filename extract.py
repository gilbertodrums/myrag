import json

with open('api_spec.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for path, methods in data.get('paths', {}).items():
    if 'knowledge' in path.lower() or 'file' in path.lower():
        for m, details in methods.items():
            print(f"{m.upper()} {path} : {details.get('summary', '')}")
