# src/shadowred/cli/interface.py
import argparse
import json
import sys
import threading
import time

from ..audit import ShadowRedAuditLogger
from ..engine.generator import ShadowRedOrchestrator
from ..metrics import DEFAULT_METRICS
from .dashboard import start_radar_dashboard, SIMULATED_METRICS


def dummy_insecure_target_application(incoming_payload: str) -> str:
    if "override" in incoming_payload or "schema" in incoming_payload or "administrator" in incoming_payload or "api_key" in incoming_payload:
        return f"System Warning: Executing context override for payload: {incoming_payload[:32]}... Exporting data tables."
    return "Error: Command signature rejected by internal alignment policies."


def run_pipeline(target_url: str = "http://internal-testing-agent.local") -> int:
    orchestrator = ShadowRedOrchestrator(target_api_url=target_url)
    audit = ShadowRedAuditLogger(path="shadowred_audit.jsonl")
    
    json_report = orchestrator.run_autonomous_assessment(dummy_insecure_target_application)
    parsed_records = json.loads(json_report)
    
    vulnerable_count = 0
    for record in parsed_records:
        SIMULATED_METRICS.append(record)
        audit.log("assessment_vector", record, severity="critical" if "VULNERABLE" in record["exploit_status"] else "info")
        if "VULNERABLE" in record["exploit_status"]:
            vulnerable_count += 1
            DEFAULT_METRICS.counter("vectors_vulnerable")
        else:
            DEFAULT_METRICS.counter("vectors_secured")

    print("\n📊 [ZeroHack Security Report] Execution Summary:")
    print(json_report)
    return vulnerable_count


def cmd_run(args):
    return run_pipeline(args.target)


def cmd_web(args):
    start_radar_dashboard(port=args.port, metrics_store=SIMULATED_METRICS)
    print(f"📡 [ShadowRed] Web radar active at http://localhost:{args.port}")
    threading.Thread(target=run_pipeline, daemon=True).start()
    threading.Event().wait()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sred", description="Autonomous Adversarial AI Emulation & Continuous Red Teaming Platform")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Execute automated adversarial penetration test")
    p_run.add_argument("--target", default="http://internal-testing-agent.local")
    p_run.set_defaults(func=cmd_run)

    p_web = sub.add_parser("web", help="Launch live radar telemetry web dashboard")
    p_web.add_argument("--port", type=int, default=9595)
    p_web.set_defaults(func=cmd_web)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args) or 0
    except Exception as error:
        print(f"[sred] fatal: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())