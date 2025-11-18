import csv
import io
import json
import os
import textwrap

import requests

STATBANK_URL = "https://api.statbank.dk/v1/data/KVPCT/CSV"


def build_request_body():
    """
    Bygger en forespørgsel til Statistikbanken.

    Du skal måske justere variabelnavne hvis Danmarks Statistik ændrer tabellen.
    Pointen er:
    - Vælg alle kommuner
    - Vælg tiden 2021
    - Vælg den række der repræsenterer samlet valgdeltagelse i procent
    """

    body = {
        "table": "KVPCT",
        "format": "CSV",
        "time": ["2021"],
        # De konkrete variable i dimensionerne kan du slå op på statistikbanken.dk for KVPCT.
        # Typisk vil der være en dimension for kommune, og en for "Result of the election".
        # Her antager vi, at dimensionerne hedder KOMMUNE og VALGTYPE, og at koden for
        # samlet valgdeltagelse i procent er "VALGDELT".
        "KOMMUNE": ["*"],
        "VALGTYPE": ["VALGDELT"],
    }
    return body


def fetch_csv():
    body = build_request_body()
    resp = requests.post(STATBANK_URL, json=body)
    resp.raise_for_status()
    return resp.text


def parse_csv_to_json(csv_text, output_path="data/kv2021_turnout.json"):
    """
    Forventer en CSV med mindst:
    - en kolonne med kommune-kode
    - en kolonne med kommune-navn
    - en kolonne med værdien i procent

    Kolonnenavne kan du se ved at printe headeren én gang, hvis det driller.
    Jeg skriver det, så det er nemt at tilpasse to-tre linjer, når du ser den faktiske fil.
    """

    # Statistikbanken bruger normalt ; som separator
    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")

    # Hjælp dig selv med at se, hvad kolonnerne hedder, første gang scriptet kører
    print("Kolonner i CSV:", reader.fieldnames)

    result = {}

    for row in reader:
        # Her skal du tilpasse til de præcise kolonnenavne.
        # Typisk vil der være en kolonne med kommune-kode og en med kommunenavn.
        # Kode kunne fx hedde "KOMKODE" eller bare "KOMMUNE".
        # Værdien kan stå i en kolonne, der typisk hedder "INDHOLD" eller lignende.

        # EKSEMPEL på noget, der ofte svarer til virkeligheden.
        # Tilpas disse tre linjer når du har set fieldnames overfor:
        kommune_kode = row["KOMKODE"]
        kommune_navn = row["KOMNAVN"]
        værdi_str = row["INDHOLD"]

        værdi = float(værdi_str.replace(",", "."))
        result[kommune_kode] = {
            "navn": kommune_navn,
            "stemmeprocent": round(værdi, 1),
        }

    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def main():
    csv_text = fetch_csv()
    parse_csv_to_json(csv_text)


if __name__ == "__main__":
    main()
