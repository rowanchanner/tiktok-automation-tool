"""
main.py — TikTok Automation Suite launcher.
Interactive menu to select and run any tool in the suite.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colorama import Fore, Style, init as colorama_init
from scripts.utils import print_banner, print_status
from scripts import config

colorama_init(autoreset=True)


def show_menu():
    """Display the main selection menu with current settings indicators."""
    headless_tag = f"{Fore.GREEN}ON" if config.HEADLESS_MODE else f"{Fore.RED}OFF"
    proxy_tag = f"{Fore.GREEN}ON" if config.USE_PROXIES else f"{Fore.RED}OFF"

    print(f"""
  {Fore.CYAN}╔══════════════════════════════════════════╗
  ║         SELECT A TOOL TO RUN             ║
  ╠══════════════════════════════════════════╣
  ║                                          ║
  ║  {Fore.GREEN}[1]{Fore.CYAN} Account Loader                     ║
  ║  {Fore.GREEN}[2]{Fore.CYAN} View Bot                           ║
  ║  {Fore.GREEN}[3]{Fore.CYAN} Like Bot                           ║
  ║  {Fore.GREEN}[4]{Fore.CYAN} Comment Bot                        ║
  ║  {Fore.GREEN}[5]{Fore.CYAN} Follow Bot                         ║
  ║                                          ║
  ║  {Fore.YELLOW}[6]{Fore.CYAN} Settings  {Fore.WHITE}Headless:{headless_tag} {Fore.WHITE}Proxy:{proxy_tag}{Fore.CYAN}  ║
  ║                                          ║
  ║  {Fore.RED}[0]{Fore.CYAN} Exit                               ║
  ║                                          ║
  ╚══════════════════════════════════════════╝{Style.RESET_ALL}
""")


def settings_menu():
    """Interactive settings panel — toggle headless & proxies, auto-saves."""
    while True:
        config.reload()
        settings = config.load_settings()

        headless_status = f"{Fore.GREEN}ON {Style.RESET_ALL}" if settings["headless_mode"] else f"{Fore.RED}OFF{Style.RESET_ALL}"
        proxy_status = f"{Fore.GREEN}ON {Style.RESET_ALL}" if settings["use_proxies"] else f"{Fore.RED}OFF{Style.RESET_ALL}"

        print(f"""
  {Fore.CYAN}╔══════════════════════════════════════════╗
  ║              S E T T I N G S             ║
  ╠══════════════════════════════════════════╣
  ║                                          ║
  ║  {Fore.YELLOW}[1]{Fore.CYAN} Headless Mode       [{headless_status}{Fore.CYAN}]            ║
  ║  {Fore.YELLOW}[2]{Fore.CYAN} Use Proxies         [{proxy_status}{Fore.CYAN}]            ║
  ║                                          ║
  ║  {Fore.WHITE}[0]{Fore.CYAN} Back to Main Menu                 ║
  ║                                          ║
  ╚══════════════════════════════════════════╝{Style.RESET_ALL}
""")

        choice = input(f"  {Fore.CYAN}Select setting to toggle: {Style.RESET_ALL}").strip()

        if choice == "1":
            settings["headless_mode"] = not settings["headless_mode"]
            config.save_settings(settings)
            config.reload()
            state = "ON" if settings["headless_mode"] else "OFF"
            print_status(f"Headless Mode → {state}  (saved)", "success")

        elif choice == "2":
            settings["use_proxies"] = not settings["use_proxies"]
            config.save_settings(settings)
            config.reload()
            state = "ON" if settings["use_proxies"] else "OFF"
            print_status(f"Use Proxies → {state}  (saved)", "success")

            if settings["use_proxies"] and not os.path.exists(config.PROXY_FILE):
                print_status(f"Note: Create 'proxies.txt' in project root with your proxies (one per line)", "warning")

        elif choice == "0":
            return

        else:
            print_status("Invalid option — pick 0-2", "error")


def main():
    """Main entry point — menu loop."""
    while True:
        print_banner()
        show_menu()

        choice = input(f"  {Fore.CYAN}Select option: {Style.RESET_ALL}").strip()

        if choice == "1":
            print_status("Launching Account Loader...\n", "action")
            from scripts.accountloader import run as run_loader
            run_loader()

        elif choice == "2":
            print_status("Launching View Bot...\n", "action")
            from scripts.viewbot import run as run_views
            run_views()

        elif choice == "3":
            print_status("Launching Like Bot...\n", "action")
            from scripts.likebot import run as run_likes
            run_likes()

        elif choice == "4":
            print_status("Launching Comment Bot...\n", "action")
            from scripts.commentbot import run as run_comments
            run_comments()

        elif choice == "5":
            print_status("Launching Follow Bot...\n", "action")
            from scripts.followbot import run as run_follows
            run_follows()

        elif choice == "6":
            settings_menu()
            continue

        elif choice == "0":
            print_status("Shutting down. 6767.\n", "info")
            sys.exit(0)

        else:
            print_status("Invalid option — pick 0-6", "error")

        input(f"\n  {Fore.CYAN}Press Enter to return to menu...{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
