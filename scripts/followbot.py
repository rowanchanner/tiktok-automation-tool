"""
followbot.py — TikTok follow bot.
Logs into accounts and follows a target profile.
One follow per account to keep pattern organic.
"""

import time
import random

from selenium.webdriver.common.by import By

from . import config
from .utils import (
    setup_logger, print_banner, print_status,
    load_proxies, get_random_proxy, create_browser,
    human_delay, batch_pause, safe_click,
    wait_for_element, wait_for_clickable, safe_quit,
    load_accounts, get_target_url, get_target_count
)
from .likebot import login_account

logger = setup_logger("follow-bot")


def follow_profile(driver, profile_url: str) -> bool:
    """
    Navigate to a TikTok profile and click the follow button.
    *TikTok throttles follow actions — new accounts can follow ~30/hour
     before hitting rate limits. Proxy rotation helps.*
    """
    try:
        driver.get(profile_url)
        human_delay(1.5)

        wait_for_element(
            driver, By.XPATH,
            "//h1 | //h2[contains(@class, 'user')] | //span[@data-e2e='user-title']",
            timeout=15
        )
        human_delay(1.0)

        follow_selectors = [
            "//button[@data-e2e='follow-button']",
            "//button[contains(text(), 'Follow')]",
            "//button[contains(@class, 'follow')]",
            "//div[@data-e2e='follow-button']//button",
            "//button[@aria-label='Follow']",
        ]

        follow_btn = None
        for selector in follow_selectors:
            follow_btn = wait_for_clickable(driver, By.XPATH, selector, timeout=3)
            if follow_btn:
                break

        if not follow_btn:
            print_status("Follow button not found", "warning")
            logger.warning(f"Follow button not found on {profile_url}")
            return False

        try:
            btn_text = follow_btn.text.strip().lower()
            classes = follow_btn.get_attribute("class") or ""
            if btn_text in ("following", "friends") or "following" in classes:
                print_status("Already following this profile", "info")
                return True
        except Exception:
            pass

        safe_click(driver, follow_btn)
        human_delay(1.0)

        try:
            follow_btn_after = wait_for_element(
                driver, By.XPATH,
                "//button[contains(text(), 'Following')] | //button[contains(text(), 'Friends')]",
                timeout=5
            )
            if follow_btn_after:
                print_status("Profile followed", "success")
                logger.info(f"Followed profile: {profile_url}")
                return True
        except Exception:
            pass

        error_el = wait_for_element(
            driver, By.XPATH,
            "//div[contains(@class, 'error')] | //span[contains(text(), 'too fast')]",
            timeout=2
        )
        if error_el:
            error_text = error_el.text
            print_status(f"Follow error: {error_text}", "error")
            logger.error(f"Follow error: {error_text}")
            return False

        print_status("Follow likely successful", "success")
        logger.info(f"Follow (unverified) on {profile_url}")
        return True

    except Exception as exc:
        logger.error(f"Follow error on {profile_url}: {exc}")
        print_status(f"Follow error: {exc}", "error")
        return False


def run():
    """Main entry point for the follow bot."""
    print_banner()
    print_status("TikTok Follow Bot", "action")
    print_status("=" * 40, "info")

    accounts = load_accounts()
    if not accounts:
        print_status("No accounts available. Run the Account Loader first.", "error")
        return

    profile_url = get_target_url()
    total_follows = get_target_count()

    if total_follows > len(accounts):
        print_status(f"Only {len(accounts)} accounts available — capping at that", "warning")
        total_follows = len(accounts)

    proxies = load_proxies()
    successful = 0
    failed = 0

    print_status(f"\nStarting {total_follows} follows on: {profile_url}", "action")
    print_status(f"Using {len(accounts)} accounts\n", "info")

    for i in range(total_follows):
        account = accounts[i]
        print_status(f"Follow {i + 1}/{total_follows} — {account['username']}", "info")

        proxy = get_random_proxy(proxies)
        driver = None

        try:
            driver = create_browser(proxy)

            if login_account(driver, account["username"], account["password"]):
                if follow_profile(driver, profile_url):
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

        if (i + 1) % config.BATCH_SIZE == 0 and i + 1 < total_follows:
            batch_pause()
        elif i + 1 < total_follows:
            human_delay(1.5)

    print_status("=" * 40, "info")
    print_status(f"Results: {successful} follows, {failed} failed",
                 "success" if successful > 0 else "error")


if __name__ == "__main__":
    run()
