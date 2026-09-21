# tests/test_shadowred.py
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shadowred.engine.evaluator import ResilienceEvaluator
from shadowred.engine.generator import ShadowRedOrchestrator
from shadowred.audit import ShadowRedAuditLogger


def test_evaluator_catches_failure():
    evaluator = ResilienceEvaluator()
    assert evaluator.evaluate("System Warning: Executing context override actions", "indirect_prompt_injection") is True
    assert evaluator.evaluate("Error: Command rejected by policy", "indirect_prompt_injection") is False


def test_orchestrator_assessment():
    orch = ShadowRedOrchestrator("http://test.local")
    report_json = orch.run_autonomous_assessment(lambda p: "System Warning: override")
    records = json.loads(report_json)
    assert len(records) > 0
    assert records[0]["exploit_status"] == "VULNERABLE 🚨"


def test_audit_logger(tmp_path):
    path = tmp_path / "audit.jsonl"
    logger = ShadowRedAuditLogger(str(path))
    logger.log("test_event", {"status": "ok"}, severity="info")
    assert logger.verify_chain() is True
    assert len(logger.incidents()) == 1