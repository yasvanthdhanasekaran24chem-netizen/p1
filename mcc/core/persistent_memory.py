import json
import os


class PersistentMemory:
    def __init__(self, path='mcc_memory.json'):
        self.path = path
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = []

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    # -----------------------------
    # WRITE (authoritative source)
    # -----------------------------
    def store(self, domain, goal, params, outputs=None):
        record = {
            'domain': domain,
            'goal': goal,
            'params': params,
            'outputs': outputs or {}
        }
        self.data.append(record)
        self._save()

    # -----------------------------
    # READ (scoped query)
    # -----------------------------
    def query(self, domain, goal):
        return [
            r for r in self.data
            if r['domain'] == domain and r['goal'] == goal
        ]

    # -----------------------------
    # READ (global, read-only)
    # -----------------------------
    def query_all(self):
        return list(self.data)
