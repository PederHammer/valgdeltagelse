import csv
import io
import json
import os

import requests

# Tabel for kommunalvalg: resultat efter område (kommune), resultat-type (VALRES) og tid
STATBANK_URL = "https://api.statbank.dk/v1/data"

def fetch_csv():
    # KVRES: kommunalvalg-resultater efter område, resultat-type (VALRES) og tid
    # Vi henter 2021, alle kommuner og to typer:
    # V  = stemmeberettigede (vælgere)
    # AS = afgivne stemmer
    body = {
        "table": "KVRES",
        "format": "CSV",
        "time": ["2021"],          # TID-variablen i tabellen
        "OMRÅDE": ["*"],           # alle kommuner
        "VALRES": ["V", "AS"],     # de rigtige ID-koder fra dit screenshot
    }

    print("Request body:", json.dumps(body, ensure_ascii=False))
    resp = requests.post(STATBANK_URL, json=body)
    print("HTTP status:", resp.status_code)
    print("Svar (første 500 tegn):")
    print(resp.text[:500])
    resp.raise_for_status()
    return resp.text







def parse_csv_to_json(csv_text, output_path="data/kv2021_turnout.json"):
    """
    Første trin: inspicér CSV'en og udregn stemmeprocent pr. kommune.

    Forventet struktur (typisk for KVRES):

    OMRÅDE;VALRES;TID;INDHOLD
    751 Syddjurs;VÆLGERE;2021;31789
    751 Syddjurs;AFGIVNE STEMMER;2021;22874
    ...

    Vi:
    - samler tal pr. kommune
    - beregner 100 * afgivne / vælgere
    - gemmer som {komkode: {navn, stemmeprocent}}
    """

    reader = csv.DictReader(io.StringIO(csv_text), delimiter=";")

    print("Kolonner i CSV:", reader.fieldnames)

    # Byg midlertidig struktur:
    # { komkode: { "navn": "...", "vælgere": X, "afgivne": Y } }
    tmp = {}

    for row in reader:
        # Se lige én række i loggen til debug
        # (men ikke for hver række - det bliver for meget)
        # Du kan kommentere dette print ud, når det virker.
        # print("ROW:", row)

        # Her skal vi måske justere feltnavne efter headeren,
        # men lad os starte med de mest sandsynlige:
        komkode = row.get("OMRÅDE") or row.get("KOMKODE")
        valgtype = row.get("VALRES")
        value_str = row.get("INDHOLD")

        if not komkode or not valgtype or value_str in (None, ""):
            continue

        # Nogle gange står kommune-koden sammen med navn (fx "751 Syddjurs")
        # I så fald splitter vi på første mellemrum.
        parts = komkode.split(" ", 1)
        if len(parts) == 2 and parts[0].isdigit():
            kode = parts[0]
            navn = parts[1]
        else:
            kode = komkode
            navn = komkode  # så har vi i det mindste noget

        try:
            value = float(value_str.replace(",", "."))
        except ValueError:
            continue

        d = tmp.setdefault(kode, {"navn": navn, "vælgere": None, "afgivne": None})

        if valgtype.upper().startswith("VÆLGERE"):
            d["vælgere"] = value
        elif "AFGIVNE" in valgtype.upper():
            d["afgivne"] = value

    result = {}
    for kode, d in tmp.items():
        vælgere = d["vælgere"]
        afgivne = d["afgivne"]
        if not vælgere or not afgivne:
            continue
        pct = 100.0 * afgivne / vælgere
        result[kode] = {
            "navn": d["navn"],
            "stemmeprocent": round(pct, 1),
        }

    os.makedirs("data", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Skrev {len(result)} kommuner til {output_path}")


def main():
    csv_text = fetch_csv()
    parse_csv_to_json(csv_text)


if __name__ == "__main__":
    main()
