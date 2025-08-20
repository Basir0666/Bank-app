
import csv
import random
from typing import List, Dict

def generate_account_number() -> str:
    # 10-digit number, not starting with 0
    first = str(random.randint(1, 9))
    rest = ''.join(str(random.randint(0,9)) for _ in range(9))
    return first + rest

def export_transactions_to_csv(account_number: str, tx_rows: List[Dict], path: str) -> str:
    filename = path or f"transactions_{account_number}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["created_at", "type", "amount", "balance_after", "note"])
        for r in tx_rows:
            writer.writerow([r["created_at"], r["type"], r["amount"], r["balance_after"], r.get("note","")])
    return filename
