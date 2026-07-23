"""
utils.py — Shared utilities for TikTok automation suite.
Browser factory, proxy loader, rate limiter, logging, human-like delays.
"""

import os
import sys
import time
import random
import json
import logging
from datetime import datetime

from colorama import Fore, Style, init as colorama_init
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    ElementClickInterceptedException, StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

from . import config

colorama_init(autoreset=True)

# ─── Logging Setup ───────────────────────────────────────────────

def setup_logger(name: str) -> logging.Logger:
    """Create a logger with file + console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

    if not logger.handlers:
        file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(name)-18s | %(levelname)-7s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)

        if config.VERBOSE_CONSOLE:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(
                "%(asctime)s | %(name)-18s | %(levelname)-7s | %(message)s",
                datefmt="%H:%M:%S"
            ))
            logger.addHandler(console_handler)

    return logger


# ─── Console Banners ─────────────────────────────────────────────

BANNER = f"""{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ████████╗██╗██╗  ██╗████████╗ ██████╗ ██╗  ██╗  ║
║              ╚══██╔══╝██║██║ ██╔╝╚══██╔══╝██╔═══██╗██║ ██╔╝  ║
║                 ██║   ██║█████╔╝    ██║   ██║   ██║█████╔╝   ║
║                 ██║   ██║██╔═██╗    ██║   ██║   ██║██╔═██╗   ║
║                 ██║   ██║██║  ██╗   ██║   ╚██████╔╝██║  ██╗  ║
║                 ╚═╝   ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝  ║
║                                                              ║
║                   A U T O M A T I O N   S U I T E           ║
║                      by SharkySolvers                        ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)


def print_status(message: str, status: str = "info"):
    """Pretty-print a status message with color coding."""
    colors = {
        "info":    Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error":   Fore.RED,
        "action":  Fore.MAGENTA,
    }
    prefix_symbols = {
        "info":    "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error":   "✗",
        "action":  "►",
    }
    color = colors.get(status, Fore.WHITE)
    symbol = prefix_symbols.get(status, "•")
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"  {Fore.WHITE}{timestamp} {color}{symbol} {message}{Style.RESET_ALL}")


# ─── Proxy Management ───────────────────────────────────────────

def load_proxies() -> list[str]:
    """Load proxies from file, one per line. Returns empty list if disabled."""
    if not config.USE_PROXIES:
        return []

    if not os.path.exists(config.PROXY_FILE):
        print_status(f"Proxy file not found: {config.PROXY_FILE}", "warning")
        return []

    with open(config.PROXY_FILE, "r", encoding="utf-8") as proxy_file:
        proxies = [
            line.strip() for line in proxy_file
            if line.strip() and not line.startswith("#")
        ]

    print_status(f"Loaded {len(proxies)} proxies", "info")
    return proxies


def get_random_proxy(proxies: list[str]) -> str | None:
    """Pick a random proxy from the pool."""
    if not proxies:
        return None
    return random.choice(proxies)


# ─── Browser Factory ─────────────────────────────────────────────

def load_cookies(driver: webdriver.Chrome):
    """Load cookies from config.COOKIE_FILE into the browser."""
    if not os.path.exists(config.COOKIE_FILE):
        return
    try:
        with open(config.COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        driver.get("https://www.tiktok.com")
        for ck in cookies:
            cookie_dict = {
                "name": ck.get("name"),
                "value": ck.get("value"),
                "domain": ck.get("domain"),
                "path": ck.get("path", "/"),
                "secure": ck.get("secure", False),
                "httpOnly": ck.get("httpOnly", False),
            }
            if ck.get("expirationDate"):
                cookie_dict["expiry"] = int(ck.get("expirationDate"))
            try:
                driver.add_cookie(cookie_dict)
            except Exception as e:
                print_status(f"Failed to add cookie {ck.get('name')}: {e}", "warning")
        driver.refresh()
    except Exception as e:
        print_status(f"Error loading cookies from {config.COOKIE_FILE}: {e}", "error")

def create_browser(proxy: str | None = None) -> webdriver.Chrome:
    """Create a Chrome instance with optional proxy and load TikTok cookies if available."""
    user_agent_factory = UserAgent()
    chrome_options = ChromeOptions()

    if config.HEADLESS_MODE:
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument(f"--user-agent={user_agent_factory.random}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.page_load_strategy = config.PAGE_LOAD_STRATEGY

    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )

    driver.implicitly_wait(config.IMPLICIT_WAIT)
    driver.set_page_load_timeout(config.BROWSER_TIMEOUT)

    # Load cookies if a cookie file is present
    if os.path.exists(config.COOKIE_FILE):
        try:
            with open(config.COOKIE_FILE, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            # Navigate to TikTok domain first to set the correct domain for cookies
            driver.get("https://www.tiktok.com")
            for ck in cookies:
                # Selenium expects certain keys; filter out unsupported ones
                cookie_dict = {
                    "name": ck.get("name"),
                    "value": ck.get("value"),
                    "domain": ck.get("domain"),
                    "path": ck.get("path", "/"),
                    "secure": ck.get("secure", False),
                    "httpOnly": ck.get("httpOnly", False),
                }
                if ck.get("expirationDate"):
                    cookie_dict["expiry"] = int(ck.get("expirationDate"))
                try:
                    driver.add_cookie(cookie_dict)
                except Exception as e:
                    # Log but continue loading other cookies
                    print(f"Failed to add cookie {ck.get('name')}: {e}")
            # Refresh after adding cookies to apply session
            driver.refresh()
        except Exception as e:
            print(f"Error loading cookies from {config.COOKIE_FILE}: {e}")

    return driver

    user_agent_factory = UserAgent()
    chrome_options = ChromeOptions()

    if config.HEADLESS_MODE:
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument(f"--user-agent={user_agent_factory.random}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.page_load_strategy = config.PAGE_LOAD_STRATEGY

    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
    )

    driver.implicitly_wait(config.IMPLICIT_WAIT)
    driver.set_page_load_timeout(config.BROWSER_TIMEOUT)

    return driver


# ─── Human-Like Delays ───────────────────────────────────────────

def human_delay(multiplier: float = 1.0):
    """Sleep for a randomized duration to mimic human behavior."""
    base_delay = random.uniform(config.MIN_ACTION_DELAY, config.MAX_ACTION_DELAY)
    jittered = base_delay * multiplier * random.uniform(0.8, 1.2)
    time.sleep(max(0.5, jittered))


def batch_pause():
    """Longer pause between batches to avoid rate limiting."""
    pause_duration = random.uniform(config.BATCH_PAUSE_MIN, config.BATCH_PAUSE_MAX)
    print_status(f"Batch pause: {pause_duration:.1f}s", "info")
    time.sleep(pause_duration)


# ─── Selenium Helpers ─────────────────────────────────────────────

def safe_click(driver: webdriver.Chrome, element, retries: int = 3):
    """Click an element with retry logic for intercepted clicks."""
    for attempt in range(retries):
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.3)
            element.click()
            return True
        except ElementClickInterceptedException:
            time.sleep(0.5)
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                if attempt == retries - 1:
                    return False
        except StaleElementReferenceException:
            return False
    return False


def wait_for_element(driver: webdriver.Chrome, by: By, value: str,
                     timeout: int = 10) -> object | None:
    """Wait for an element to be present and return it, or None on timeout."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None


def wait_for_clickable(driver: webdriver.Chrome, by: By, value: str,
                       timeout: int = 10) -> object | None:
    """Wait for an element to be clickable and return it, or None on timeout."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        return element
    except TimeoutException:
        return None


def safe_quit(driver: webdriver.Chrome | None):
    """Safely quit a browser instance."""
    if driver:
        try:
            driver.quit()
        except Exception:
            pass


# ─── Account File I/O ────────────────────────────────────────────

def save_account(username: str, password: str, email: str):
    """Append account credentials to the output file."""
    with open(config.ACCOUNT_OUTPUT_FILE, "a", encoding="utf-8") as account_file:
        account_file.write(f"{username}:{password}:{email}\n")
    print_status(f"Account saved: {username}", "success")


def load_accounts() -> list[dict]:
    """Load accounts from file. Returns list of {username, password, email}.
    Falls back to cookie session as a pseudo-account when cookies.json exists."""
    accounts = []

    if os.path.exists(config.ACCOUNT_OUTPUT_FILE):
        with open(config.ACCOUNT_OUTPUT_FILE, "r", encoding="utf-8") as account_file:
            for line in account_file:
                parts = line.strip().split(":")
                if len(parts) >= 3:
                    accounts.append({
                        "username": parts[0],
                        "password": parts[1],
                        "email": parts[2]
                    })

    # No password-based accounts — fall back to cookie session
    if not accounts and os.path.exists(config.COOKIE_FILE):
        try:
            with open(config.COOKIE_FILE, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            session_cookie = next(
                (c for c in cookies if c.get("name") == "sessionid"), None
            )
            if session_cookie:
                print_status("No accounts.txt — using cookie session as account", "info")
                accounts.append({
                    "username": "cookie-session",
                    "password": "",
                    "email": "cookie-auth",
                    "cookie_auth": True
                })
            else:
                print_status("Cookie file has no sessionid — cannot use as account", "warning")
        except Exception as exc:
            print_status(f"Error reading cookie file: {exc}", "error")

    if not accounts:
        print_status("No accounts file found and no valid cookies. Load accounts or cookies first.", "error")

    return accounts


def get_target_url() -> str:
    """Prompt user for a TikTok video or profile URL."""
    while True:
        url = input(f"\n  {Fore.CYAN}Enter TikTok URL: {Style.RESET_ALL}").strip()
        if "tiktok.com" in url:
            return url
        print_status("Invalid URL — must contain tiktok.com", "error")


def get_target_count() -> int:
    """Prompt user for how many actions to perform."""
    while True:
        try:
            count = int(input(f"  {Fore.CYAN}How many actions: {Style.RESET_ALL}").strip())
            if count > 0:
                return count
            print_status("Must be a positive number", "error")
        except ValueError:
            print_status("Enter a valid number", "error")
