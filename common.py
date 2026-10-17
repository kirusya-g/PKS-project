import ipaddress
import json
import random
import threading
import zlib
from datetime import datetime, timezone

SENSORS = {
    "ThermoNode": [("temperature", "f", -50.0, 60.0, 1), ("humidity", "f", 0.0, 100.0, 1),
                   ("dew_point", "f", -50.0, 60.0, 1), ("pressure", "f", 800.0, 1100.0, 2)],
    "WindSense": [("wind_speed", "f", 0.0, 50.0, 1), ("")]
}