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