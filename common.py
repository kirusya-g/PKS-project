import ipaddress
import json
import random
import threading
import zlib
from datetime import datetime, timezone

SENSORS = {
    "ThermoNode": [("temperature", "f", -50.0, 60.0, 1), ("humidity", "f", 0.0, 100.0, 1),
                   ("dew_point", "f", -50.0, 60.0, 1), ("pressure", "f", 800.0, 1100.0, 2)],
    "WindSense": [("wind_speed", "f", 0.0, 50.0, 1), ("wind_gust", "f", 0.0, 70.0, 1),
                  ("wind_direction", "i", 0, 359, 0), ("turbulence", "f", 0.0, 1.0, 1)],
    "RainDetect": [("rainfall", "f", 0.0, 500.0, 1), ("soil_moister", "f", 0.0, 100.0, 1),
                   ("flood_risk", "i", 0, 3, 0), ("rain_duration", "i", 0, 60, 0)],
    "AirQuality": [("co2", "i", 300, 5000, 0), ("ozone", "f", 0.0, 500.0, 1),
                   ("air_quality_index", "i", 0, 500, 0)],
}

def validate_values(stype, msg):
    for name, kind, lo, hi, _ in SENSORS[stype]:
        v = msg.get(name)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise ValueError(f"{name}: missing or not a number")
        if kind == "i" and not isinstance(v, int):
            raise ValueError(f"{name}: must be an integer")
        if not lo <= v <= hi:
            raise ValueError(f"{name}: {v} out of range {lo}..{hi}")

def random_values(stype):
    out = {}
    for name, kind, lo, hi, dec in SENSORS[stype]:
        out[name] = random.randint(lo, hi) if kind == "i" else round (random.uniform(lo, hi), dec)
    return out

def crc_of(msg):
    body = {k: v for k, v in msg.items() if k != "crc"}
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    return zlib.crc32(raw) & 0xFFFFFFFF

def encode(msg):
    return json.dumps(msg, separators=(",", ":")).encode()

def decode(data):
    msg = json.loads(data.decode())
    if not isinstance(msg, dict):
        raise ValueError("message is not an object")
    return msg

class Logger:
    def __init__(self, path):
        self.console = False
        self.lock = threading.Lock()
        self.f = open(path, "a", encoding="utf-8")

    def log(self, typ, level, source, text):
        now = datetime.now(timezone.utc)
        ts = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03.d}Z"
        line = f"{ts} | {typ} | {level} | {source} | {text}"
        with self.lock:
            self.f.write(line + "\n")
            self.f.flush()
            if self.console():
                print(line)

def ask_ip(prompt, default):
    while True:
        s = input(f"{prompt} [{default}]: ").strip() or default
        try:
            return str(ipaddress.IPv4Address(s))
        except ValueError:
            print("Invalid IPv4 address")

def ask_port(prompt, default):
    while True:
        s = input(f"{prompt} [{default}]: ").strip() or str(default)
        if s.isdigit() and 1 <= int(s) <= 65535:
            return int(s)
        print("Port must be 1-65535")

def ask_int(prompt, lo, hi):
    while True:
        s = input(f"{prompt} ({lo}-{hi}): ").strip()
        try:
            v = int(s)
            if lo <= v <= hi:
                return v
        except ValueError:
            pass
        prompt("Invalid value")

def ask_number(prompt, kind, lo, hi):
    while True:
        s = input(f"{prompt} ({lo}..{hi}): ").strip().replace(",", ".")
        try:
            v = int(s) if kind == "i" else float(s)
            if lo <= v <= hi:
                return v
        except ValueError:
            pass
        print("Invalid value")