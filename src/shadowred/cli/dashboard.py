# src/shadowred/cli/dashboard.py
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import List

from ..metrics import DEFAULT_METRICS

SIMULATED_METRICS: List[dict] = []


class ShadowRedTelemetryHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/api/v1/telemetry":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({
                "engine": "ShadowRed",
                "metrics": DEFAULT_METRICS.snapshot(),
                "data": SIMULATED_METRICS
            }).encode())
        elif self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(DEFAULT_METRICS.prometheus_text().encode())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = f"""
            <html>
                <head><title>ShadowRed Enterprise Radar</title>
                <style>
                    body {{ font-family: monospace; background: #080000; color: #ff3333; padding: 30px; }}
                    h1 {{ color: #ff3333; text-shadow: 0 0 10px rgba(255,51,51,0.5); }}
                    .card {{ background: #1a0000; border: 1px solid #4d0000; padding: 20px; border-radius: 6px; margin-bottom: 20px; }}
                    .metric {{ font-size: 24px; color: #00ffcc; }}
                    a {{ color: #00ffcc; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
                </head>
                <body>
                    <h1>🥷 ShadowRed // Autonomous Adversarial AI Emulation Radar</h1>
                    <div class="card">
                        <p>Status: <span style="color:#00ffcc;">SWARM ACTIVE // CONTINUOUS PENTESTING</span></p>
                        <p>Evaluated Exploit Vectors: <span class="metric">{len(SIMULATED_METRICS)}</span></p>
                    </div>
                    <div class="card">
                        <h3>📊 Telemetry & Analytics</h3>
                        <p><a href="/api/v1/telemetry">JSON Telemetry Stream (/api/v1/telemetry)</a></p>
                        <p><a href="/metrics">Prometheus Metrics (/metrics)</a></p>
                    </div>
                </body>
            </html>
            """
            self.wfile.write(html.encode())


def start_radar_dashboard(port: int = 9595, metrics_store: list = None) -> HTTPServer:
    global SIMULATED_METRICS
    if metrics_store is not None:
        SIMULATED_METRICS = metrics_store
    server = HTTPServer(("", port), ShadowRedTelemetryHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"📡 [ShadowRed UI Platform] Live metrics dashboard accessible at http://localhost:{port}")
    return server