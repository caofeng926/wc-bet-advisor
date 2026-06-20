import sqlite3
db = sqlite3.connect(r'D:\v2rayN-windows-64-desktop\v2rayN-windows-64\guiConfigs\guiNDB.db')
cur = db.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print('tables:', tables)
for t in tables:
    cur.execute(f"PRAGMA table_info({t})")
    cols = [r[1] for r in cur.fetchall()]
    print(f'  {t}: {cols}')
    cur.execute(f"SELECT * FROM {t} LIMIT 3")
    for row in cur.fetchall():
        print('    row keys:', list(row))
