import csv
import io
import json
import os

import requests

STATBANK_URL = "https://api.statbank.dk/v1/data/KVPCT/CSV"


def build_request_body():
    body = {
        "table": "KVPCT",
        "format": "CSV",
        "time": ["2021"],
        # Tilpas dimensioner hvis nødvendigt. KVPCT kan have andre navne.
        "KOMMUNE": ["*"],
        "VALGTYPE": ["VALGDELT"],  # samlet valgdeltagelse i pct.
    }
    return body


def fetch_csv():
    body = build_request_body()
    resp = requests.post(STATBANK_URL, json=body)
    resp.raise_for_status()
    return resp.text


def parse_csv_to_json(csv_text, output_path="data/kv2021_turnout.json"):
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")

    # Print kolonnenavne til GitHub Actions log
    print("Kolonner i CSV:", reader.fieldnames)

    result = {}

    for row in reader:
        # Her skal vi tilpasse til de rigtige feltnavne.
        # Første gang lader vi det gerne fejle, ser fieldnames i loggen,
        # og retter disse tre linjer.
        kommune_kode = row["KOMKODE"]
        kommune_navn = row["KOMNAVN"]
        value_str = row["INDHOLD"]

        value = float(value_str.replace(",", "."))
        result[kommune_kode] = {
            "navn": kommune_navn,
            "stemmeprocent": round(value, 1),
        }

    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    csv_text = fetch_csv()
    parse_csv_to_json(csv_text)


if __name__ == "__main__":
    main()
