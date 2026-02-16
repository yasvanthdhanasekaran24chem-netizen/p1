from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from .schema import RunResult


class CognitiveMemoryStore:
    def __init__(self, path: str | Path = "cognitive_memory.jsonl"):
        self.path = Path(path)

    def append(self, result: RunResult) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")

    def load_all(self) -> List[RunResult]:
        if not self.path.exists():
            return []

        out: List[RunResult] = []
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if "parameters" not in row:
                    row["parameters"] = {}
                out.append(RunResult(**row))
        return out
