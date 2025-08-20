from .db import get_conn
import bcrypt
import pandas as pd
from datetime import datetime

class AccountService:
    def __init__(self):
        self.conn = get_conn()

    # ---------- Core: Create / Login ----------

    def create_account(self, name, email, pin):
        cursor = self.conn.cursor(dictionary=True)

        # Insert user
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        user_id = cursor.lastrowid

        # Hash PIN
        pin_hash = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()

        # Simple account number generation
        account_number = f"AC{1000 + user_id}"

        # Insert account
        cursor.execute(
            "INSERT INTO accounts (account_number, user_id, pin_hash, balance) VALUES (%s, %s, %s, %s)",
            (account_number, user_id, pin_hash, 0.0)
        )

        self.conn.commit()
        cursor.close()
        return account_number

    def login(self, account_number, pin):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        account = cursor.fetchone()

        if not account:
            cursor.close()
            return False

        if account["is_locked"]:
            print("🚫 Your account is locked. Contact admin.")
            cursor.close()
            return False

        if bcrypt.checkpw(pin.encode(), account["pin_hash"].encode()):
            # Reset failed attempts on success
            cursor.execute(
                "UPDATE accounts SET failed_attempts = 0 WHERE id = %s",
                (account["id"],)
            )
            self.conn.commit()
            cursor.close()
            return True
        else:
            # Wrong PIN handling with lockout after 3 attempts
            new_attempts = account["failed_attempts"] + 1
            if new_attempts >= 3:
                cursor.execute(
                    "UPDATE accounts SET failed_attempts = %s, is_locked = 1 WHERE id = %s",
                    (new_attempts, account["id"])
                )
                print("🚫 Account locked after 3 failed login attempts.")
            else:
                cursor.execute(
                    "UPDATE accounts SET failed_attempts = %s WHERE id = %s",
                    (new_attempts, account["id"])
                )
                print(f"❌ Wrong PIN. Attempts left: {3 - new_attempts}")
            self.conn.commit()
            cursor.close()
            return False

    def is_account_locked(self, account_number):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT is_locked FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row and row["is_locked"] == 1

    def unlock_account(self, account_number):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "UPDATE accounts SET is_locked = 0, failed_attempts = 0 WHERE account_number = %s",
            (account_number,)
        )
        self.conn.commit()
        cursor.close()
        print(f"🔓 Account {account_number} has been unlocked by admin.")

    # ---------- Money Ops + Transactions ----------

    def deposit(self, account_number, amount):
        if amount <= 0:
            print("❌ Amount must be positive.")
            return

        cursor = self.conn.cursor(dictionary=True)

        # Update balance
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_number = %s",
            (amount, account_number)
        )

        # Fetch updated balance & account id
        cursor.execute(
            "SELECT id, balance FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        acc = cursor.fetchone()
        if not acc:
            self.conn.rollback()
            cursor.close()
            print("❌ Account not found.")
            return

        # Log transaction
        cursor.execute(
            "INSERT INTO transactions (account_id, type, amount, balance_after, note) VALUES (%s, %s, %s, %s, %s)",
            (acc["id"], "DEPOSIT", amount, acc["balance"], "Deposit made")
        )

        self.conn.commit()
        cursor.close()
        print(f"✅ Deposited {amount}")

    def withdraw(self, account_number, amount):
        if amount <= 0:
            print("❌ Amount must be positive.")
            return

        cursor = self.conn.cursor(dictionary=True)

        # Check balance
        cursor.execute(
            "SELECT id, balance FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        acc = cursor.fetchone()
        if not acc:
            cursor.close()
            print("❌ Account not found.")
            return

        if acc["balance"] < amount:
            cursor.close()
            print("❌ Insufficient funds.")
            return

        # Update balance
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_number = %s",
            (amount, account_number)
        )
        new_balance = acc["balance"] - amount

        # Log transaction
        cursor.execute(
            "INSERT INTO transactions (account_id, type, amount, balance_after, note) VALUES (%s, %s, %s, %s, %s)",
            (acc["id"], "WITHDRAW", amount, new_balance, "Withdrawal made")
        )

        self.conn.commit()
        cursor.close()
        print(f"✅ Withdrawn {amount}")

    def get_balance(self, account_number):
        cursor = self.conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT balance FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        row = cursor.fetchone()
        cursor.close()
        return row["balance"] if row else 0.0

    def get_transactions(self, account_number, limit=10):
        cursor = self.conn.cursor(dictionary=True)

        # Get account id
        cursor.execute(
            "SELECT id FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        acc = cursor.fetchone()
        if not acc:
            cursor.close()
            return []

        # Fetch transactions
        cursor.execute(
            "SELECT type, amount, balance_after, created_at "
            "FROM transactions WHERE account_id = %s "
            "ORDER BY created_at DESC LIMIT %s",
            (acc["id"], limit)
        )
        txs = cursor.fetchall()
        cursor.close()
        return txs

    def export_transactions_csv(self, account_number, limit=50):
        cursor = self.conn.cursor(dictionary=True)

        # Get account id
        cursor.execute(
            "SELECT id FROM accounts WHERE account_number = %s",
            (account_number,)
        )
        acc = cursor.fetchone()
        if not acc:
            cursor.close()
            print("❌ Account not found.")
            return None

        # Fetch transactions
        cursor.execute(
            "SELECT created_at, type, amount, balance_after "
            "FROM transactions WHERE account_id = %s "
            "ORDER BY created_at DESC LIMIT %s",
            (acc["id"], limit)
        )
        txs = cursor.fetchall()
        cursor.close()

        if not txs:
            print("📭 No transactions to export.")
            return None

        # Export via pandas
        df = pd.DataFrame(txs)
        filename = f"{account_number}_statement_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        df.to_csv(filename, index=False)

        print(f"✅ Transactions exported to {filename}")
        return filename

    # ---------- Admin Dashboard ----------

    def get_admin_stats(self):
        cursor = self.conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        cursor.execute("SELECT COUNT(*) AS total_accounts FROM accounts")
        total_accounts = cursor.fetchone()["total_accounts"]

        cursor.execute("SELECT COUNT(*) AS locked_accounts FROM accounts WHERE is_locked = 1")
        locked_accounts = cursor.fetchone()["locked_accounts"]

        cursor.execute("SELECT COALESCE(SUM(balance), 0) AS total_balance FROM accounts")
        total_balance = cursor.fetchone()["total_balance"] or 0

        cursor.close()

        return {
            "total_users": total_users,
            "total_accounts": total_accounts,
            "locked_accounts": locked_accounts,
            "total_balance": total_balance
        }
