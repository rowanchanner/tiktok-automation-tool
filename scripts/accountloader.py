"""
accountloader.py — TikTok manual account loader.
Loads accounts from input/accounts.txt, validates format,
lets you add new accounts interactively.
"""

import os
import json
import shutil

from . import config
from .utils import (
    print_banner, print_status, load_accounts, save_account
)


def show_accounts():
    """Display all loaded accounts with index numbers."""
    accounts = load_accounts()
    if not accounts:
        print_status("No accounts loaded yet", "warning")
        print_status(f"Add accounts to: {config.ACCOUNT_INPUT_FILE}", "info")
        return

    print_status(f"Loaded {len(accounts)} account(s):\n", "info")
    for i, account in enumerate(accounts, 1):
        if account.get("cookie_auth"):
            print(f"    [{i:>3}]  🍪 cookie-session  |  (cookie auth)  |  no password needed")
        else:
            masked_pw = account["password"][:3] + "*" * max(0, len(account["password"]) - 3)
            print(f"    [{i:>3}]  {account['username']}  |  {masked_pw}  |  {account['email']}")
    print()


def add_accounts_interactive():
    """Prompt user to add accounts one at a time."""
    print_status("Add accounts — enter details below", "action")
    print_status("Leave username blank to stop\n", "info")

    added = 0
    while True:
        username = input("    Username/Email: ").strip()
        if not username:
            break

        password = input("    Password:       ").strip()
        if not password:
            print_status("Password cannot be empty", "error")
            continue

        # Email is optional — use username as fallback
        email = input("    Email (optional): ").strip() or username

        save_account(username, password, email)
        added += 1

    if added > 0:
        print_status(f"Added {added} account(s)", "success")
    else:
        print_status("No accounts added", "info")


def show_cookie_status():
    """Display current cookie file status and key session info."""
    if not os.path.exists(config.COOKIE_FILE):
        print_status(f"No cookie file found at: {config.COOKIE_FILE}", "warning")
        print_status("Drop your cookies.json into the input/ folder to enable cookie login", "info")
        return

    try:
        with open(config.COOKIE_FILE, "r", encoding="utf-8") as fh:
            cookies = json.load(fh)
        session_cookie = next((c for c in cookies if c.get("name") == "sessionid"), None)
        print_status(f"Cookie file loaded: {len(cookies)} cookies", "success")
        if session_cookie:
            import datetime
            exp = session_cookie.get("expirationDate")
            if exp:
                exp_dt = datetime.datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M")
                print_status(f"Session expires: {exp_dt}", "info")
            print_status(f"Session ID (first 8): {session_cookie['value'][:8]}...", "info")
        else:
            print_status("Warning: no sessionid cookie found — may not be a valid TikTok session", "warning")
    except Exception as exc:
        print_status(f"Error reading cookie file: {exc}", "error")


def import_cookie_file():
    """Copy a cookies.json from a user-specified path into input/."""
    from colorama import Fore, Style
    src = input(f"\n  {Fore.CYAN}Path to your cookies.json: {Style.RESET_ALL}").strip().strip('"')
    if not os.path.exists(src):
        print_status(f"File not found: {src}", "error")
        return
    try:
        shutil.copy2(src, config.COOKIE_FILE)
        print_status(f"Copied to {config.COOKIE_FILE}", "success")
        show_cookie_status()
    except Exception as exc:
        print_status(f"Copy failed: {exc}", "error")


def clear_cookie_file():
    """Delete the active cookie file."""
    if not os.path.exists(config.COOKIE_FILE):
        print_status("No cookie file to remove", "info")
        return
    os.remove(config.COOKIE_FILE)
    print_status("Cookie file removed", "success")


def import_from_file():
    """
    Import accounts from a file with auto-detected format.
    Supports:
      username:password
      username:password:email
      email:password
    One account per line. Lines starting with # are skipped.
    """
    print_status(f"Import from: {config.ACCOUNT_INPUT_FILE}", "action")

    if not os.path.exists(config.ACCOUNT_INPUT_FILE):
        print_status(f"File not found: {config.ACCOUNT_INPUT_FILE}", "error")
        print_status("Create the file and add accounts in format:", "info")
        print_status("  username:password", "info")
        print_status("  username:password:email", "info")
        return

    imported = 0
    skipped = 0

    with open(config.ACCOUNT_INPUT_FILE, "r", encoding="utf-8") as fh:
        for line_num, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(":")
            if len(parts) == 2:
                username, password = parts
                email = username
            elif len(parts) >= 3:
                username, password, email = parts[0], parts[1], parts[2]
            else:
                print_status(f"Line {line_num}: bad format — skipping", "warning")
                skipped += 1
                continue

            if not username.strip() or not password.strip():
                print_status(f"Line {line_num}: empty username or password — skipping", "warning")
                skipped += 1
                continue

            save_account(username.strip(), password.strip(), email.strip())
            imported += 1

    print_status(f"Imported {imported} accounts ({skipped} skipped)", "success" if imported > 0 else "warning")


def run():
    """Main entry point for the account loader."""
    from colorama import Fore, Style

    print_banner()
    print_status("TikTok Account Loader", "action")
    print_status("=" * 40, "info")

    while True:
        # Cookie status indicator for menu header
        if os.path.exists(config.COOKIE_FILE):
            cookie_tag = f"{Fore.GREEN}ACTIVE"
        else:
            cookie_tag = f"{Fore.RED}NONE"

        print(f"""
  {Fore.CYAN}╔══════════════════════════════════════════╗
  ║          ACCOUNT MANAGEMENT              ║
  ╠══════════════════════════════════════════╣
  ║                                          ║
  ║  {Fore.GREEN}[1]{Fore.CYAN} View loaded accounts               ║
  ║  {Fore.GREEN}[2]{Fore.CYAN} Add accounts manually              ║
  ║  {Fore.GREEN}[3]{Fore.CYAN} Import from input/accounts.txt     ║
  ║                                          ║
  ║  {Fore.YELLOW}[4]{Fore.CYAN} Cookie status  [{cookie_tag}{Fore.CYAN}]              ║
  ║  {Fore.YELLOW}[5]{Fore.CYAN} Import cookie file                ║
  ║  {Fore.YELLOW}[6]{Fore.CYAN} Clear cookie file                 ║
  ║                                          ║
  ║  {Fore.WHITE}[0]{Fore.CYAN} Back                               ║
  ║                                          ║
  ╚══════════════════════════════════════════╝{Style.RESET_ALL}
""")

        choice = input(f"  {Fore.CYAN}Select option: {Style.RESET_ALL}").strip()

        if choice == "1":
            show_accounts()
        elif choice == "2":
            add_accounts_interactive()
        elif choice == "3":
            import_from_file()
        elif choice == "4":
            show_cookie_status()
        elif choice == "5":
            import_cookie_file()
        elif choice == "6":
            clear_cookie_file()
        elif choice == "0":
            return
        else:
            print_status("Invalid option — pick 0-6", "error")


if __name__ == "__main__":
    run()
