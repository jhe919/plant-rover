#!/usr/bin/env python3
"""
HTTP -> Serial bridge for Pi + Arduino control.

Run on the Pi:
  python src/pi_arduino_bridge.py --port /dev/ttyACM0 --baud 115200

Then POST commands from the Mac:
  curl -X POST http://<pi_ip>:9000/command -H "Content-Type: application/json" -d '{"cmd":"STOP"}'
"""
from __future__ import annotations

import argparse
import json
from typing import Optional

from flask import Flask, jsonify, request
from flask_cors import CORS
import serial

app = Flask(__name__)
CORS(app)

ser: Optional[serial.Serial] = None


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Bridge HTTP commands to Arduino over Serial.")
    ap.add_argument("--port", default="/dev/ttyACM0",
                    help="Serial device (e.g. /dev/ttyACM0 or /dev/ttyUSB0).")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--listen-port", type=int, default=9000)
    return ap.parse_args()


@app.route("/command", methods=["POST"])
def command():
    if ser is None or not ser.is_open:
        return jsonify({"ok": False, "error": "serial not open"}), 500
    payload = request.get_json(silent=True) or {}
    cmd = payload.get("cmd")
    if not cmd:
        return jsonify({"ok": False, "error": "missing cmd"}), 400
    print(f"[bridge] cmd={cmd}", flush=True)
    ser.write((cmd.strip() + "\n").encode("utf-8"))
    return jsonify({"ok": True, "cmd": cmd})


@app.route("/status")
def status():
    return jsonify({
        "ok": ser is not None and ser.is_open,
        "port": None if ser is None else ser.port,
        "baud": None if ser is None else ser.baudrate,
    })


def main() -> None:
    args = parse_args()
    global ser
    ser = serial.Serial(args.port, args.baud, timeout=1)
    app.run(host=args.host, port=args.listen_port, threaded=True)


if __name__ == "__main__":
    main()
