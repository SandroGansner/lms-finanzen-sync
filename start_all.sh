#!/bin/bash

# Pfad zu deinem Projektverzeichnis
PROJECT_DIR="/Users/sandrogansner/sync_project"

# Aktiviere die virtuelle Umgebung
source "$PROJECT_DIR/venv/bin/activate"

# Starte alle Skripte gleichzeitig im Hintergrund
python "$PROJECT_DIR/sync_purchases.py" &
python "$PROJECT_DIR/sync_expenses.py" &
python "$PROJECT_DIR/sync_campaigns.py" &

# Warte kurz, um sicherzustellen, dass alle Prozesse gestartet sind
sleep 1

echo "Alle Skripte wurden gestartet. Sie laufen im Hintergrund."
