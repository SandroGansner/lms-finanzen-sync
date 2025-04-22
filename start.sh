#!/bin/bash
python sync_purchases.py &
python sync_expenses.py &
python sync_campaigns.py &
