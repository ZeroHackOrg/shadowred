# src/shadowred/audit.py
import hashlib
import json
import threading
import time
from pathlib import Path
from typing import List, Optional


class ShadowRedAuditLogger:
    def __init__(self, path: str = "shadowred_audit.jsonl"):
        self.path = Path(path)
        self._lock = threading.Lock()
        self._bonsai: List[dict] = []
        self._tail_hash = self._load_existing()

    def _load_existing(self) -> Optional[str]:
        if not self.path.exists():
            return None
        for line in self.path.read_text().splitlines():
            if not line.strip():
                continue
            self._bonsai.append(json.loads(line))
        return self._bonsai[-1]["record_hash"] if self._bonsai else None

    def log(self, event: str, details: dict, severity: str = "warning") -> dict:
        previous = self._tail_hash
        payload = {"event": event, "severity": severity, "details": details, "ts": time.time()}
        record = {
            "payload": payload,
            "previous_hash": previous,
            "record_hash": self._hash_record(payload, previous),
        }
        with self._lock:
            self._tail_hash = record["record_hash"]
            self._bonsai.append(record)
            self._append(record)
        return record

    def _append(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a") as handle:
            handle.write(json.dumps(record) + "\n")

    @staticmethod
    def _hash_record(payload: dict, previous: Optional[str]) -> str:
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        chain = f"{previous or ''}:{blob}"
        return hashlib.sha256(chain.encode()).hexdigest()

    def incidents(self) -> List[dict]:
        return list(self._bonsai)

    def verify_chain(self) -> bool:
        previous = None
        for line in self.path.read_text().splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            expected = self._hash_record(record["payload"], previous)
            if record["record_hash"] != expected:
                return False
            previous = record["record_hash"]
        return True