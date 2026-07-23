"""
likebot.py — TikTok like bot.
Logs into accounts from accounts.txt and likes a target video.
Each account likes once to keep the engagement pattern organic.
"""

import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from . import config
from .utils import (
    setup_logger, print_banner, print_status,
    load_proxies, get_random_proxy, create_browser,
    human_delay, batch_pause, safe_click,
    wait_for_element, wait_for_clickable, safe_quit,
    load_accounts, get_target_url, get_target_count,
    load_cookies
)

logger = setup_logger("like-bot")

TIKTOK_LOGIN_URL = "https://www.tiktok.com/login/phone-or-email/email"


def is_logged_in(driver) -> bool:
    """
    Check if the current browser session is already authenticated.
    Looks for profile-specific DOM elements that only appear when logged in.
    """
    try:
        # TikTok renders these elements only for authenticated sessions
        logged_in_indicators = [
            "//div[@data-e2e='profile-icon']",
            "//a[@data-e2e='nav-profile']",
            "//span[@data-e2e='profile-icon']",
            "//div[contains(@class, 'avatar') and not(contains(@class, 'guest'))]",
        ]
        for selector in logged_in_indicators:
            el = wait_for_element(driver, By.XPATH, selector, timeout=4)
            if el:
                return True
        return False
    except Exception:
        return False


def login_account(driver, username: str, password: str) -> bool:
    """
    Log into TikTok. If a cookie session is already active (injected by
    create_browser via cookies.json), skip password login entirely.
    *TikTok's login flow may trigger CAPTCHA or 2FA — this handles
     the base case only. CAPTCHA solving requires external service integration.*
    """
    try:
        # Cookie session already injected by create_browser — verify it
        import os
        from . import config as _config
        if os.path.exists(_config.COOKIE_FILE):
            driver.get("https://www.tiktok.com/foryou")
            human_delay(2.0)
            if is_logged_in(driver):
                print_status(f"Cookie session active — skipping password login for {username}", "success")
                logger.info(f"Cookie login active: {username}")
                return True
            print_status(f"Cookie session invalid or expired — falling back to password login", "warning")

        driver.get(TIKTOK_LOGIN_URL)
        human_delay(1.5)

        login_input = wait_for_element(
            driver, By.XPATH,
            "//input[@name='username'] | //input[@placeholder='Email or username'] | //input[@type='text']",
            timeout=15
        )
        if not login_input:
            print_status(f"Login input not found for {username}", "warning")
            return False

        login_input.clear()
        for char in username:
            login_input.send_keys(char)
            time.sleep(random.uniform(0.02, 0.06))
        human_delay(0.5)

        password_input = wait_for_element(
            driver, By.XPATH,
            "//input[@name='password'] | //input[@type='password']",
            timeout=10
        )
        if not password_input:
            print_status(f"Password input not found for {username}", "warning")
            return False

        password_input.clear()
        for char in password:
            password_input.send_keys(char)
            time.sleep(random.uniform(0.02, 0.06))
        human_delay(0.5)

        submit_btn = wait_for_clickable(
            driver, By.XPATH,
            "//button[@type='submit'] | //button[contains(text(), 'Log in')]",
            timeout=10
        )
        if submit_btn:
            safe_click(driver, submit_btn)
            human_delay(2.0)
        else:
            password_input.send_keys(Keys.RETURN)
            human_delay(2.0)

        if "login" not in driver.current_url.lower() or "foryou" in driver.current_url.lower():
            print_status(f"Logged in as {username}", "success")
            logger.info(f"Login successful: {username}")
            return True

        print_status(f"Login may have failed for {username}", "warning")
        logger.warning(f"Uncertain login state for {username}")
        return False

    except Exception as exc:
        logger.error(f"Login error for {username}: {exc}")
        print_status(f"Login error: {exc}", "error")
        return False


def like_video(driver, video_url: str) -> bool:
    """Navigate to a video and click the like button."""
    try:
        driver.get(video_url)
        human_delay(1.5)

        wait_for_element(driver, By.TAG_NAME, "video", timeout=15)
        human_delay(1.0)

        like_selectors = [
            "//button[@data-e2e='like-icon']",
            "//span[@data-e2e='like-icon']",
            "//div[contains(@class, 'like')]//button",
            "//button[contains(@class, 'like')]",
            "//span[contains(@class, 'like-icon')]/..",
        ]

        like_btn = None
        for selector in like_selectors:
            like_btn = wait_for_clickable(driver, By.XPATH, selector, timeout=3)
            if like_btn:
                break

        if not like_btn:
            like_btn = wait_for_clickable(
                driver, By.XPATH,
                "//button[@aria-label='Like'] | //button[@aria-label='like video']",
                timeout=5
            )

        if like_btn:
            try:
                classes = like_btn.get_attribute("class") or ""
                aria = like_btn.get_attribute("aria-pressed") or ""
                if "active" in classes or "liked" in classes or aria == "true":
                    print_status("Already liked this video", "info")
                    return True
            except Exception:
                pass

            safe_click(driver, like_btn)
            human_delay(0.5)
            print_status("Video liked", "success")
            logger.info(f"Liked video: {video_url}")
            return True
        else:
            print_status("Like button not found", "warning")
            logger.warning(f"Like button not found on {video_url}")
            return False

    except Exception as exc:
        logger.error(f"Like error on {video_url}: {exc}")
        print_status(f"Like error: {exc}", "error")
        return False


def run():
    """Main entry point for the like bot."""
    print_banner()
    print_status("TikTok Like Bot", "action")
    print_status("=" * 40, "info")

    accounts = load_accounts()
    if not accounts:
        print_status("No accounts available. Run the Account Loader first.", "error")
        return

    video_url = get_target_url()
    total_likes = get_target_count()

    if total_likes > len(accounts):
        print_status(f"Only {len(accounts)} accounts available — capping at that", "warning")
        total_likes = len(accounts)

    proxies = load_proxies()
    successful = 0
    failed = 0

    print_status(f"\nStarting {total_likes} likes on: {video_url}", "action")
    print_status(f"Using {len(accounts)} accounts\n", "info")

    for i in range(total_likes):
        account = accounts[i]
        print_status(f"Like {i + 1}/{total_likes} — account: {account['username']}", "info")

        proxy = get_random_proxy(proxies)
        driver = None

        try:
            driver = create_browser(proxy)

            if login_account(driver, account["username"], account["password"]):
                if like_video(driver, video_url):
                    successful += 1
                else:
                    failed += 1
            else:
                failed += 1

        except Exception as exc:
            print_status(f"Error: {exc}", "error")
            failed += 1

        finally:
            safe_quit(driver)

        if (i + 1) % config.BATCH_SIZE == 0 and i + 1 < total_likes:
            batch_pause()
        elif i + 1 < total_likes:
            human_delay(1.5)

    print_status("=" * 40, "info")
    print_status(f"Results: {successful} likes, {failed} failed", "success" if successful > 0 else "error")


if __name__ == "__main__":
    run()
