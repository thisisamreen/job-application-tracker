# ============================================================
# GOOGLE SHEET ACCESS (service account)
#
# The service account email must have access to the sheet (Share -> Editor).
# Usage (from repo root):
#   python src/sheet.py
# ============================================================

import glob
import os

import gspread
from dotenv import dotenv_values

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WORKSHEET = "Job Applications"


def get_worksheet():
    env = dotenv_values(os.path.join(ROOT, ".env"))
    creds = glob.glob(os.path.join(ROOT, "creds", "*.json"))
    if len(creds) != 1:
        raise SystemExit("Expected exactly one service account JSON in creds/")

    client = gspread.service_account(filename=creds[0])
    return client.open_by_key(env["TRACKER_SHEET"]).worksheet(WORKSHEET)


def read_rows():
    return get_worksheet().get_all_values()


if __name__ == "__main__":
    rows = read_rows()
    print(f"{len(rows) - 1} rows, {len(rows[0])} columns")
    print("Header:", rows[0])
    for row in rows[1:]:
        print(row)
