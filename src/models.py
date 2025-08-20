
from typing import Optional, List, Dict, Tuple
from mysql.connector import MySQLConnection, cursor

# Low-level DB functions (no business rules). Use parameterized queries only.

def create_user(conn: MySQLConnection, name: str, email: str) -> int:
    sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
    with conn.cursor() as cur:
        cur.execute(sql, (name, email))
        return cur.lastrowid

def get_user_by_email(conn: MySQLConnection, email: str) -> Optional[Dict]:
    sql = "SELECT id, name, email, created_at FROM users WHERE email=%s"
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, (email,))
        return cur.fetchone()

def create_account(conn: MySQLConnection, user_id: int, account_number: str, pin_hash: str) -> int:
    sql = "INSERT INTO accounts (user_id, account_number, pin_hash) VALUES (%s, %s, %s)"
    with conn.cursor() as cur:
        cur.execute(sql, (user_id, account_number, pin_hash))
        return cur.lastrowid

def get_account_by_number(conn: MySQLConnection, account_number: str) -> Optional[Dict]:
    sql = "SELECT * FROM accounts WHERE account_number=%s"
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, (account_number,))
        return cur.fetchone()

def update_account_failed_attempts(conn: MySQLConnection, account_id: int, attempts: int, lock: bool):
    sql = "UPDATE accounts SET failed_attempts=%s, is_locked=%s WHERE id=%s"
    with conn.cursor() as cur:
        cur.execute(sql, (attempts, 1 if lock else 0, account_id))

def update_account_balance(conn: MySQLConnection, account_id: int, new_balance: float):
    sql = "UPDATE accounts SET balance=%s WHERE id=%s"
    with conn.cursor() as cur:
        cur.execute(sql, (new_balance, account_id))

def insert_transaction(conn: MySQLConnection, account_id: int, t_type: str, amount: float, balance_after: float, note: str=""):
    sql = "INSERT INTO transactions (account_id, type, amount, balance_after, note) VALUES (%s, %s, %s, %s, %s)"
    with conn.cursor() as cur:
        cur.execute(sql, (account_id, t_type, amount, balance_after, note))

def get_last_transactions(conn: MySQLConnection, account_id: int, limit: int=5) -> List[Dict]:
    sql = "SELECT created_at, type, amount, balance_after, note FROM transactions WHERE account_id=%s ORDER BY id DESC LIMIT %s"
    with conn.cursor(dictionary=True) as cur:
        cur.execute(sql, (account_id, limit))
        return cur.fetchall()
