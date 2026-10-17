import secrets
import socket
import threading
import time

from common import *

IDLE_AFTER = 15
KA_INTERVAL = 5
KA_MAX = 3

class Session:
    def __init__(self, stype, sid, addr, reg_seq):
        self.stype, self.sid, self.addr, self.reg_seq = stype, sid, addr, reg_seq
        self.label = f"{stype}:{sid}"
        self.token = secrets.token_hex(4)
        self.state = "ACTIVE"
        self.last_data = time.monotonic()
        self.last_ka = 0.0
        self.ka_unanswered = 0
        self.last_seq = None
        self.values = None
        self.reg_ack = None

class Server:
    def __init__(self, log):
        self.log = log
        self.sock = None
        self.running = False
        self.sessions = {}
        self.drop = {}
        self.lock = threading.RLock()
        self._seq = 0

    def sys(self, level, text):
        self.log.log("SYSTEM", level, "SERVER", text)

    def send(self, msg, addr):
        data = encode(msg)
        try:
            self.sock.sendto(data, addr)
        except OSError as e:
            self.sys("ERROR", f"Send to {addr} failed: {e}")
            return
        self.log.log("MESSAGE", "INFO", "SERVER", f"Sent to {addr[0]:{addr[1]} {data.decode()}}")

    def reject(self, msg, addr, reason):
        self.send({"type": "REJECT", "seq": self.next_seq(),
                   "ack_for": msg.get("seq"), "reason": reason}, addr)