import csv
import io
import json
import os

import requests

STATBANK_URL = "https://api.statbank.dk/v1/data/KVRES/CSV"


def build_request_body():
    # KVRES: Valg til kommunalbestyrelser efter område, valgresultat (VALRES) og tid
    # Vi tager:
    # - 2021
    # - alle kommuner (OMRÅDE="*")
    # - alle valgresultat-typer (VALRES="*") – vi filtrerer senere i Python
    return {
        "table": "KVRES",
        "format": "CSV",
        "time": ["2021"],
        "OMRÅDE": ["*"],
        "VALRES": ["*"],
    }


def fetch_csv():
    body = build_request_body()
    resp = requests.post(STATBANK_URL, json=body)
    print("HTTP status:", resp.status_code)
    print("Svar (første 500 tegn):")
    print(resp.text[:500])
    resp.raise_for_status()
    return resp.text



def parse_csv_to_json(csv_text, output_path="data/kv2021_turnout.json"):
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")

    # Print kolonne-navne til loggen
    print("Kolonner i CSV:", reader.fieldnames)

    # Print et par eksemplerækker til loggen, så vi kan se strukturen
    for i, row in enumerate(reader):
        print(f"Eksempel-række {i}:", row)
        if i >= 4:  # max 5 rækker
            break

    # Skriv midlertidig tom JSON-fil, så scriptet ikke fejler
    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)



def main():
    csv_text = fetch_csv()
    parse_csv_to_json(csv_text)


if __name__ == "__main__":
    main()
