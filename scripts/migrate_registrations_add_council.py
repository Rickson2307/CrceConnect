import sqlite3, os

p = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'registrations.db')
print('registrations.db path:', p)
if not os.path.exists(p):
    print('No registrations.db found, nothing to do.')
    raise SystemExit(0)

conn = sqlite3.connect(p)
cur = conn.cursor()
# Check columns
cur.execute("PRAGMA table_info('Registration')")
cols = [r[1] for r in cur.fetchall()]
print('Columns in Registration table:', cols)
if 'council' in [c.lower() for c in cols]:
    print('council column already present (case-insensitive). nothing to do.')
else:
    try:
        print('Adding council column...')
        cur.execute("ALTER TABLE Registration ADD COLUMN council TEXT")
        conn.commit()
        print('council column added.')
    except Exception as e:
        print('Failed to add column:', e)
        raise

conn.close()
print('Done.')
