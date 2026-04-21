#!/usr/bin/env python
"""Polls until a real MySQL/MariaDB connection succeeds."""
import os
import sys
import time

import MySQLdb
from dotenv import load_dotenv

load_dotenv()

host = os.environ.get("DB_HOST", "127.0.0.1")
port = int(os.environ.get("DB_PORT", 3306))
user = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]
db = os.environ["DB_NAME"]

for attempt in range(30):
    try:
        MySQLdb.connect(host=host, port=port, user=user, passwd=password, db=db)
        print("db is ready")
        sys.exit(0)
    except MySQLdb.OperationalError as e:
        print(f"waiting for db... ({e})")
        time.sleep(1)

print("db did not become ready in time")
sys.exit(1)
