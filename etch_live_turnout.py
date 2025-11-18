import json
import os
from datetime import datetime

os.makedirs("data", exist_ok=True)

data = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "kommuner": {}
}

with open("data/live_turnout.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
