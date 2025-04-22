import os
from dotenv import load_dotenv
import requests

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

# Teste die Verbindung zur Tabelle "purchases"
response = requests.get(f"{SUPABASE_URL}/rest/v1/purchases", headers=headers)

# Gib die Antwort aus
print(f"Statuscode: {response.status_code}")
print(f"Antwort: {response.text}")
