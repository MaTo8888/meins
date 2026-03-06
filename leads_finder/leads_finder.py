#!/usr/bin/env python3
"""
Lead-Finder: Sanitär, Heizung & Elektriker Firmen in Deutschland
Sucht Firmen via Google Places API und speichert sie in Google Sheets.
Keine Duplikate über mehrere Ausführungen.
"""

import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import googlemaps
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

# ── Konfiguration ──────────────────────────────────────────────────────────────

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GOOGLE_SHEET_ID     = os.getenv("GOOGLE_SHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")

TARGET_LEADS = 100   # Wie viele neue Leads pro Durchlauf gesucht werden

SEARCH_TERMS = [
    "Sanitär Installateur",
    "Sanitärbetrieb",
    "Heizungsinstallateur",
    "Heizungsbau",
    "Elektriker",
    "Elektrobetrieb",
    "Sanitär Heizung",
    "SHK Betrieb",
]

GERMAN_CITIES = [
    "Berlin", "Hamburg", "München", "Köln", "Frankfurt am Main",
    "Stuttgart", "Düsseldorf", "Leipzig", "Dortmund", "Essen",
    "Bremen", "Dresden", "Hannover", "Nürnberg", "Duisburg",
    "Bochum", "Wuppertal", "Bielefeld", "Bonn", "Münster",
    "Mannheim", "Karlsruhe", "Augsburg", "Wiesbaden", "Freiburg",
    "Erfurt", "Rostock", "Kassel", "Mainz", "Saarbrücken",
    "Potsdam", "Würzburg", "Heidelberg", "Ingolstadt", "Ulm",
    "Aachen", "Braunschweig", "Kiel", "Magdeburg", "Oberhausen",
    "Lübeck", "Chemnitz", "Halle", "Mönchengladbach", "Gelsenkirchen",
    "Krefeld", "Darmstadt", "Trier", "Regensburg", "Paderborn",
]

SHEET_HEADERS = [
    "company_name", "contact_name", "phone", "email",
    "status", "meeting_at", "next_action_date", "notes", "place_id",
]

# ── Google Sheets ──────────────────────────────────────────────────────────────

def connect_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    return sheet


def ensure_headers(sheet):
    existing = sheet.row_values(1)
    if existing != SHEET_HEADERS:
        sheet.insert_row(SHEET_HEADERS, 1)
        print("✓ Kopfzeile eingefügt")


def load_existing_place_ids(sheet):
    try:
        col_index = SHEET_HEADERS.index("place_id") + 1
        values = sheet.col_values(col_index)
        return set(values[1:])  # Kopfzeile überspringen
    except Exception:
        return set()


def append_lead(sheet, lead: dict):
    row = [lead.get(h, "") for h in SHEET_HEADERS]
    sheet.append_row(row, value_input_option="USER_ENTERED")

# ── E-Mail Scraping ────────────────────────────────────────────────────────────

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LeadBot/1.0)"}


def find_email_on_website(url: str) -> str:
    if not url:
        return ""
    emails = set()
    pages = [url, url.rstrip("/") + "/impressum", url.rstrip("/") + "/kontakt"]
    for page in pages:
        try:
            resp = requests.get(page, timeout=8, headers=HEADERS)
            if resp.status_code == 200:
                found = EMAIL_REGEX.findall(resp.text)
                for e in found:
                    # Häufige False-Positives filtern
                    if not any(x in e for x in ["example", "domain", "email", "test", ".png", ".jpg"]):
                        emails.add(e.lower())
            time.sleep(0.5)
        except Exception:
            pass
    if emails:
        return sorted(emails)[0]
    return ""

# ── Google Places Suche ────────────────────────────────────────────────────────

def search_companies(gmaps, seen_ids: set, target: int) -> list:
    results = []
    cities = GERMAN_CITIES.copy()
    random.shuffle(cities)
    terms = SEARCH_TERMS.copy()
    random.shuffle(terms)

    for city in cities:
        for term in terms:
            if len(results) >= target:
                return results

            query = f"{term} {city}"
            print(f"  Suche: {query}")

            try:
                response = gmaps.places(query=query, language="de", region="de")
            except Exception as e:
                print(f"  API-Fehler: {e}")
                time.sleep(2)
                continue

            page_results = response.get("results", [])
            next_page_token = response.get("next_page_token")

            for place in page_results:
                if len(results) >= target:
                    break
                place_id = place.get("place_id", "")
                if place_id in seen_ids:
                    continue

                lead = extract_lead(gmaps, place_id)
                if lead:
                    seen_ids.add(place_id)
                    results.append(lead)
                    print(f"  ✓ {lead['company_name']} ({lead['phone'] or 'keine Tel.'})")

            # Nächste Seite abrufen (falls vorhanden)
            if next_page_token and len(results) < target:
                time.sleep(2)  # Google verlangt kurze Pause
                try:
                    response2 = gmaps.places(
                        query=query, language="de", region="de",
                        page_token=next_page_token
                    )
                    for place in response2.get("results", []):
                        if len(results) >= target:
                            break
                        place_id = place.get("place_id", "")
                        if place_id in seen_ids:
                            continue
                        lead = extract_lead(gmaps, place_id)
                        if lead:
                            seen_ids.add(place_id)
                            results.append(lead)
                            print(f"  ✓ {lead['company_name']} ({lead['phone'] or 'keine Tel.'})")
                except Exception:
                    pass

            time.sleep(1)  # API-Rate-Limit respektieren

    return results


def extract_lead(gmaps, place_id: str) -> dict | None:
    try:
        details = gmaps.place(
            place_id=place_id,
            fields=["name", "formatted_phone_number", "website"],
            language="de",
        ).get("result", {})
    except Exception as e:
        print(f"  Detail-Fehler: {e}")
        return None

    name = details.get("name", "")
    phone = details.get("formatted_phone_number", "")
    website = details.get("website", "")

    if not name:
        return None

    email = find_email_on_website(website)

    return {
        "company_name": name,
        "contact_name": "",
        "phone": phone,
        "email": email,
        "status": "",
        "meeting_at": "",
        "next_action_date": "",
        "notes": "",
        "place_id": place_id,
    }

# ── Hauptprogramm ──────────────────────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  Lead-Finder: Sanitär | Heizung | Elektriker")
    print("=" * 55)

    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("GOOGLE_MAPS_API_KEY fehlt in .env")
    if not GOOGLE_SHEET_ID:
        raise ValueError("GOOGLE_SHEET_ID fehlt in .env")

    print("\n[1/4] Verbinde mit Google Sheets …")
    sheet = connect_sheet()
    ensure_headers(sheet)

    print("[2/4] Lade bereits gespeicherte Leads …")
    seen_ids = load_existing_place_ids(sheet)
    print(f"      {len(seen_ids)} bestehende Einträge gefunden")

    print(f"\n[3/4] Suche {TARGET_LEADS} neue Firmen …\n")
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    new_leads = search_companies(gmaps, seen_ids, TARGET_LEADS)

    print(f"\n[4/4] Speichere {len(new_leads)} neue Leads in Google Sheets …")
    for i, lead in enumerate(new_leads, 1):
        append_lead(sheet, lead)
        print(f"      [{i}/{len(new_leads)}] {lead['company_name']}")
        time.sleep(0.3)  # Sheets-API-Rate-Limit

    print(f"\n✅ Fertig! {len(new_leads)} neue Leads gespeichert.")
    print(f"   Google Sheet: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}")


if __name__ == "__main__":
    main()
