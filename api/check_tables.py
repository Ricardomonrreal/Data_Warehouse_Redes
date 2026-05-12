import os
import sys
from db_config import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
for row in cur.fetchall():
    print(row[0])
cur.close()
conn.close()
