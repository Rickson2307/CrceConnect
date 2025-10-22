import sqlite3, os
p=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'registrations.db')
print('db path:', p)
if not os.path.exists(p):
    print('registrations.db missing')
    raise SystemExit(0)
conn=sqlite3.connect(p)
cur=conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('tables:', cur.fetchall())
try:
    cur.execute('SELECT id,event_id,event_name,council,name,roll_no,created_at FROM Registration ORDER BY created_at DESC LIMIT 20')
    rows=cur.fetchall()
    print('rows:', len(rows))
    for r in rows:
        print(r)
except Exception as e:
    print('error', e)
conn.close()
