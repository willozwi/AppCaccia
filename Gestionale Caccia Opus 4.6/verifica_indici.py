import sqlite3

conn = sqlite3.connect('gestionale_caccia.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT name, tbl_name 
    FROM sqlite_master 
    WHERE type='index' AND name LIKE 'idx_%' 
    ORDER BY tbl_name, name
""")

indices = cursor.fetchall()
print(f'Indici creati: {len(indices)}')
print()

# Raggruppa per tabella
tables = {}
for name, table in indices:
    if table not in tables:
        tables[table] = []
    tables[table].append(name)

for table in sorted(tables.keys()):
    print(f'{table}:')
    for idx in tables[table]:
        print(f'  - {idx}')

conn.close()
