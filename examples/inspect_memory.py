import json

with open('mcc_memory.json', 'r') as f:
    data = json.load(f)

print('--- MEMORY CONTENT ---')
for entry in data:
    print(entry['domain'], entry['goal'], entry['best_candidate']['params'])
