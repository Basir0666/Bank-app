Bank App (Python + MySQL)

A command-line banking system built with Python and MySQL.
Features account creation, secure PIN-based login, deposits, withdrawals, transaction history, CSV export, and admin tools.

Features

-Create a new bank account with unique account number
-Secure login with hashed PIN (bcrypt)
-Automatic account lock after 3 failed login attempts
-Deposit & Withdraw money with balance updates
-View recent transaction history
-Export transactions to CSV (via Pandas)
-Admin Unlock (reset locked accounts)
-Admin Dashboard (view total users, accounts, locked accounts, and total bank balance)

Tech Stack

Python 3.10+

MySQL 8+

Libraries:

mysql-connector-python (DB connection)

bcrypt (PIN security)

pandas (CSV export)

colorama (optional: colored CLI output)

Setup Instructions

1️) Clone Repository
git clone https://github.com/Basir0666/bank-app.git
cd bank-app

2️) Setup Virtual Environment
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux

3️) Install Dependencies
pip install -r requirements.txt

4️) Configure Database

Open MySQL Workbench (or terminal).

Run the following:

CREATE DATABASE bank_app;
CREATE USER 'bank_user'@'localhost' IDENTIFIED BY 'bank_pass123';
GRANT ALL PRIVILEGES ON bank_app.\* TO 'bank_user'@'localhost';
FLUSH PRIVILEGES;

USE bank_app;

CREATE TABLE users (
id INT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR(100) NOT NULL,
email VARCHAR(120) NOT NULL UNIQUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
id INT AUTO_INCREMENT PRIMARY KEY,
account_number VARCHAR(20) NOT NULL UNIQUE,
user_id INT NOT NULL,
pin_hash VARCHAR(100) NOT NULL,
balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
is_locked BOOLEAN NOT NULL DEFAULT 0,
failed_attempts INT NOT NULL DEFAULT 0,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE transactions (
id INT AUTO_INCREMENT PRIMARY KEY,
account_id INT NOT NULL,
type ENUM('DEPOSIT','WITHDRAW','TRANSFER_IN','TRANSFER_OUT') NOT NULL,
amount DECIMAL(12,2) NOT NULL,
balance_after DECIMAL(12,2) NOT NULL,
note VARCHAR(255),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (account_id) REFERENCES accounts(id)
);

5️) Create .env File

Inside project root, create a .env:

DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=bank_user
DB_PASSWORD=bank_pass123
DB_NAME=bank_app

Run the Application

python -m src.cli

Main Menu:
=== Bank App (Python + MySQL) ===

1. Create Account
2. Login (for protected actions)
3. Admin Unlock Account
4. Admin Dashboard
5. Exit

Admin Tools

Unlock Account → Use code 0666

Dashboard → Shows total users, total accounts, locked accounts, total balance

Sample Transaction Export

When you choose Export Transactions to CSV, a file like:

AC1001_statement_2025-08-20_12-45-12.csv

will be created with columns: created_at, type, amount, balance_after.

Future Improvements

Add monthly interest auto-credit

Add fund transfers between accounts

Add REST API / Web UI

Author

Basir (GitHub: @Basir0666)
