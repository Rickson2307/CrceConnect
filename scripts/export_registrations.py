"""
Export registrations grouped by council into a CSV file.
Usage: run this script from the repository root with the workspace python:
    C:/Users/WIN10/Desktop/CrceConnect/.venv/Scripts/python.exe scripts/export_registrations.py
"""
import csv
import sqlite3
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
reg_db = os.path.join(basedir, 'registrations.db')

if not os.path.exists(reg_db):
    print('No registrations.db found at', reg_db)
    raise SystemExit(1)

conn = sqlite3.connect(reg_db)
cur = conn.cursor()

# Query registrations ordered by council then created_at
cur.execute('SELECT council, event_name, name, class_name, year, roll_no, created_at FROM Registration ORDER BY council, created_at DESC')
rows = cur.fetchall()

out_path = os.path.join(basedir, 'registrations_export.csv')
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Council','Event','Name','Class','Year','RollNo','RegisteredAt'])
    for r in rows:
        writer.writerow(r)

print('Exported', len(rows), 'registrations to', out_path)
conn.close()