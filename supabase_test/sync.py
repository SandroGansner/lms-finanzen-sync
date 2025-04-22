import os
import requests
import pandas as pd
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

# Lade die Umgebungsvariablen aus der .env-Datei
load_dotenv()

# Hole die Werte aus der .env-Datei
SUPABASE_URL = os.getenv("SUPABASE_URL")
API_KEY = os.getenv("API_KEY")

# Setze die Header für die Anfrage
headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Funktion zum Abrufen von Daten aus einer Supabase-Tabelle
def fetch_data(table_name):
    try:
        response = requests.get(f"{SUPABASE_URL}/rest/v1/{table_name}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Fehler beim Abrufen von {table_name}: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Fehler beim Abrufen von {table_name}: {e}")
        return []

# Funktion zum Herunterladen eines Belegs
def download_receipt(receipt_path, local_path):
    try:
        if receipt_path:
            # Vollständige URL zum Beleg
            receipt_url = f"{SUPABASE_URL}/storage/v1/object/{receipt_path}"
            # Füge die Header mit dem API-Schlüssel hinzu
            response = requests.get(receipt_url, headers=headers)
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                print(f"Beleg heruntergeladen: {local_path}")
            else:
                print(f"Fehler beim Herunterladen des Belegs {receipt_path}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Fehler beim Herunterladen des Belegs {receipt_path}: {e}")

# Funktion zur Synchronisation der Einkäufe
def sync_purchases():
    print(f"Starte Synchronisation der Einkäufe: {datetime.now()}")
    purchases = fetch_data("purchases")
    if not purchases:
        print("Keine Einkäufe gefunden.")
        return

    # Konvertiere die Daten in ein DataFrame
    df_purchases = pd.DataFrame(purchases)
    if df_purchases.empty:
        print("DataFrame ist leer.")
        return

    # Konvertiere das Datum und erstelle eine Spalte für Monat/Jahr
    df_purchases['date'] = pd.to_datetime(df_purchases['date'])
    df_purchases['month_year'] = df_purchases['date'].dt.strftime('%Y_%m')

    # Gruppiere nach Kreditkarte und Monat
    grouped = df_purchases.groupby(['cardUsed', 'month_year'])

    # Erstelle oder aktualisiere Excel-Dateien und Belege-Ordner
    for (card, month_year), group in grouped:
        # Erstelle den Ordner für die Excel-Dateien
        excel_dir = f"exports/Einkäufe/{card.replace(' ', '_')}/{month_year}"
        os.makedirs(excel_dir, exist_ok=True)

        # Erstelle den Ordner für die Belege
        receipts_dir = f"exports/Belege/Belege_{card.replace(' ', '_')}_{month_year}"
        os.makedirs(receipts_dir, exist_ok=True)

        # Wähle die relevanten Spalten für die Excel-Datei
        excel_data = group[[
            'invoiceIssuer', 'itemName', 'account', 'kst', 'project', 'vatRate', 'price'
        ]].copy()
        excel_data.insert(0, 'Beleg', '')  # Beleg-Spalte (leer)
        excel_data['BETRAG EUR'] = ''  # BETRAG EUR (leer)

        # Benenne die Spalten um
        excel_data.columns = [
            'Beleg', 'Rechnungssteller', 'Text', 'Kontierung Konto', 'KST', 'Projekt', 'VAT', 'BETRAG CHF', 'BETRAG EUR'
        ]

        # Berechne die Summen
        sum_row = excel_data[['BETRAG CHF']].sum()
        sum_row['Beleg'] = 'TOTAL'
        sum_row['Rechnungssteller'] = ''
        sum_row['Text'] = ''
        sum_row['Kontierung Konto'] = ''
        sum_row['KST'] = ''
        sum_row['Projekt'] = ''
        sum_row['VAT'] = ''
        sum_row['BETRAG EUR'] = ''

        # Füge die Summenzeile hinzu
        excel_data = pd.concat([excel_data, pd.DataFrame([sum_row])], ignore_index=True)

        # Speichere die Excel-Datei
        filename = f"{excel_dir}/Einkauf_{card.replace(' ', '_')}_{month_year}.xlsx"
        try:
            excel_data.to_excel(filename, index=False)
            print(f"Excel-Datei erstellt/aktualisiert: {filename}")
        except Exception as e:
            print(f"Fehler beim Erstellen/Aktualisieren der Excel-Datei {filename}: {e}")

        # Lade die Belege herunter
        for index, row in group.iterrows():
            receipt_path = row['receiptPath']
            if receipt_path:
                receipt_filename = receipt_path.split('/')[-1]
                local_path = f"{receipts_dir}/{receipt_filename}"
                download_receipt(receipt_path, local_path)

# Hauptfunktion zur Synchronisation
def sync_all():
    sync_purchases()

# Plane die Synchronisation täglich um 2:00 Uhr
schedule.every().day.at("02:00").do(sync_all)

# Teste die Synchronisation sofort beim Start
sync_all()

# Starte den Scheduler
print("Starte Synchronisation... Drücke Ctrl+C zum Beenden.")
while True:
    schedule.run_pending()
    time.sleep(1)
