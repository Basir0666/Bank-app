from .services import AccountService

ADMIN_CODE = "0666"  

def main():
    service = AccountService()

    while True:
        print("\n=== Bank App (Python + MySQL) ===\n")
        print("1) Create Account")
        print("2) Login (for protected actions)")
        print("3) Admin Unlock Account")
        print("4) Admin Dashboard")
        print("5) Exit")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            name = input("Enter your name: ").strip()
            email = input("Enter your email: ").strip()
            pin = input("Set a 4-digit PIN: ").strip()
            account_number = service.create_account(name, email, pin)
            print(f"✅ Account created! Your account number is {account_number}")

        elif choice == "2":
            acc_no = input("Enter your account number: ").strip()

            # Retry login loop
            while True:
                pin = input("Enter your PIN: ").strip()
                success = service.login(acc_no, pin)

                if success:
                    print("✅ Login successful!")
                    # Authenticated account menu
                    while True:
                        print("\n--- Account Menu ---")
                        print("1) Deposit")
                        print("2) Withdraw")
                        print("3) Check Balance")
                        print("4) View Transaction History")
                        print("5) Export Transactions to CSV")
                        print("6) Logout")

                        sub_choice = input("\nChoose: ").strip()

                        if sub_choice == "1":
                            amount = float(input("Enter amount to deposit: "))
                            service.deposit(acc_no, amount)

                        elif sub_choice == "2":
                            amount = float(input("Enter amount to withdraw: "))
                            service.withdraw(acc_no, amount)

                        elif sub_choice == "3":
                            bal = service.get_balance(acc_no)
                            print(f"💰 Current Balance: {bal}")

                        elif sub_choice == "4":
                            txs = service.get_transactions(acc_no)
                            if not txs:
                                print("📭 No transactions yet.")
                            else:
                                print("\n📜 Last Transactions:")
                                for t in txs:
                                    print(f"- {t['created_at']} | {t['type']} | {t['amount']} | Balance: {t['balance_after']}")

                        elif sub_choice == "5":
                            service.export_transactions_csv(acc_no)

                        elif sub_choice == "6":
                            print("👋 Logged out.")
                            break

                        else:
                            print("❌ Invalid choice.")
                    break  # exit retry loop after logout

                else:
                    if service.is_account_locked(acc_no):
                        print("🚫 Account locked. Returning to main menu.")
                        break
                    else:
                        print("🔁 Please try again.")

        elif choice == "5":
            print("👋 Goodbye!")
            break

        elif choice == "3":
            admin_code = input("Enter admin unlock code: ").strip()
            if admin_code == ADMIN_CODE:
                acc_no = input("Enter account number to unlock: ").strip()
                service.unlock_account(acc_no)
            else:
                print("❌ Incorrect admin code. Access denied.")

        elif choice == "4":
            admin_code = input("Enter admin code: ").strip()
            if admin_code == ADMIN_CODE:
                stats = service.get_admin_stats()
                print("\n📊 Admin Dashboard")
                print(f"👥 Total Users: {stats['total_users']}")
                print(f"🏦 Total Accounts: {stats['total_accounts']}")
                print(f"🔒 Locked Accounts: {stats['locked_accounts']}")
                print(f"💰 Total Bank Balance: {stats['total_balance']}")
            else:
                print("❌ Incorrect admin code. Access denied.")

        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
