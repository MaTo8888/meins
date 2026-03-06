# Lead-Finder Einrichtung (Schritt für Schritt)

## Was du brauchst
- Python 3.10 oder neuer → https://python.org/downloads
- Ein Google-Konto

---

## Schritt 1 — Google Cloud Projekt einrichten

1. Gehe zu https://console.cloud.google.com
2. Klicke oben auf **"Projekt auswählen"** → **"Neues Projekt"**
3. Gib einen Namen ein (z.B. `lead-finder`) → **Erstellen**

---

## Schritt 2 — APIs aktivieren

Im Google Cloud Projekt:

1. Linkes Menü → **"APIs & Dienste"** → **"Bibliothek"**
2. Suche und aktiviere folgende APIs:
   - **Places API**
   - **Google Sheets API**
   - **Google Drive API**

---

## Schritt 3 — API Key für Google Maps

1. Linkes Menü → **"APIs & Dienste"** → **"Anmeldedaten"**
2. **"+ Anmeldedaten erstellen"** → **"API-Schlüssel"**
3. Kopiere den Schlüssel → in `.env` eintragen als `GOOGLE_MAPS_API_KEY`

---

## Schritt 4 — Service Account für Google Sheets

1. **"+ Anmeldedaten erstellen"** → **"Dienstkonto"**
2. Name eingeben (z.B. `lead-finder-bot`) → Fertig
3. Klicke auf das erstellte Dienstkonto
4. Reiter **"Schlüssel"** → **"Schlüssel hinzufügen"** → **JSON**
5. Die heruntergeladene JSON-Datei umbenennen in `service_account.json`
6. Diese Datei in den `leads_finder/` Ordner kopieren

---

## Schritt 5 — Google Sheet vorbereiten

1. Öffne https://sheets.new → neues leeres Sheet
2. Das Sheet mit dem Service Account teilen:
   - Öffne die `service_account.json` → kopiere den Wert bei `"client_email"`
     (sieht so aus: `lead-finder-bot@dein-projekt.iam.gserviceaccount.com`)
   - Im Sheet: **Teilen** → diese E-Mail einfügen → Rolle: **Bearbeiter**
3. Die Sheet-ID aus der URL kopieren:
   - URL: `https://docs.google.com/spreadsheets/d/DIESE_ID/edit`
   - In `.env` eintragen als `GOOGLE_SHEET_ID`

---

## Schritt 6 — .env Datei erstellen

Im `leads_finder/` Ordner:

```bash
cp .env.example .env
```

Dann `.env` öffnen und deine Werte eintragen:
```
GOOGLE_MAPS_API_KEY=AIza...dein_key
GOOGLE_SHEET_ID=1BxiM...deine_sheet_id
SERVICE_ACCOUNT_FILE=service_account.json
```

---

## Schritt 7 — Python-Pakete installieren

Terminal im `leads_finder/` Ordner öffnen:

```bash
pip install -r requirements.txt
```

---

## Schritt 8 — Starten!

```bash
python leads_finder.py
```

Das Skript:
- Sucht 100 neue Firmen (Sanitär, Heizung, Elektriker) in ganz Deutschland
- Versucht E-Mail-Adressen von den Firmen-Websites zu finden
- Trägt alles ins Google Sheet ein
- **Wiederholt keine bereits gespeicherten Firmen**

Einfach mehrfach ausführen — jedes Mal kommen neue Leads dazu!

---

## Kosten

| Service | Kosten |
|---|---|
| Google Places API | $17 pro 1.000 Suchen (ca. $1–2 pro 100 Leads) |
| Google Sheets API | Kostenlos |

Google gibt monatlich **$200 Guthaben** — für normale Nutzung reicht das oft aus.

---

## Häufige Fehler

**`GOOGLE_MAPS_API_KEY fehlt`** → `.env` Datei nicht erstellt oder Key nicht eingetragen

**`403 Forbidden`** → Places API nicht aktiviert (Schritt 2)

**`SpreadsheetNotFound`** → Sheet-ID falsch oder Service Account hat keinen Zugriff (Schritt 5)
