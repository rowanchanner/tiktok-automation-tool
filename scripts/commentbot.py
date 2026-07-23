"""
commentbot.py — TikTok comment bot.
Logs into accounts and posts comments from the configured comment pool
on a target video. One comment per account per video.
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
    load_accounts, get_target_url, get_target_count
)
from .likebot import login_account

logger = setup_logger("comment-bot")


def post_comment(driver, video_url: str, comment_text: str) -> bool:
    """
    Navigate to a video and post a comment.
    *TikTok may restrict commenting on new accounts or after rapid commenting.
     Rate limiting via config.BATCH_SIZE and delays is critical.*
    """
    try:
        driver.get(video_url)
        human_delay(1.5)

        wait_for_element(driver, By.TAG_NAME, "video", timeout=15)
        human_delay(1.0)

        comment_selectors = [
            "//div[@data-e2e='comment-input']",
            "//div[contains(@class, 'comment-input')]//div[@contenteditable='true']",
            "//div[@contenteditable='true' and contains(@class, 'comment')]",
            "//textarea[contains(@placeholder, 'comment')]",
            "//div[@role='textbox' and contains(@class, 'comment')]",
        ]

        comment_input = None
        for selector in comment_selectors:
            comment_input = wait_for_clickable(driver, By.XPATH, selector, timeout=3)
            if comment_input:
                break

        if not comment_input:
            comment_icon = wait_for_clickable(
                driver, By.XPATH,
                "//button[@data-e2e='comment-icon'] | //span[@data-e2e='comment-icon'] | //button[@aria-label='Comments']",
                timeout=5
            )
            if comment_icon:
                safe_click(driver, comment_icon)
                human_delay(1.5)

                for selector in comment_selectors:
                    comment_input = wait_for_clickable(driver, By.XPATH, selector, timeout=3)
                    if comment_input:
                        break

        if not comment_input:
            print_status("Comment input not found", "warning")
            logger.warning(f"Comment input not found on {video_url}")
            return False

        safe_click(driver, comment_input)
        human_delay(0.5)

        for char in comment_text:
            comment_input.send_keys(char)
            time.sleep(random.uniform(0.03, 0.10))

        human_delay(0.8)

        post_btn = wait_for_clickable(
            driver, By.XPATH,
            "//button[@data-e2e='comment-post'] | //button[contains(text(), 'Post')] | //div[@data-e2e='comment-post']",
            timeout=5
        )

        if post_btn:
            safe_click(driver, post_btn)
        else:
            comment_input.send_keys(Keys.RETURN)

        human_delay(1.5)

        try:
            page_source = driver.page_source
            if comment_text[:20] in page_source:
                print_status(f"Comment posted: \"{comment_text[:40]}...\"", "success")
                logger.info(f"Comment posted on {video_url}: {comment_text}")
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
            print_status(f"Comment error: {error_text}", "error")
            logger.error(f"Comment error: {error_text}")
            return False

        print_status(f"Comment likely posted: \"{comment_text[:40]}\"", "success")
        logger.info(f"Comment (unverified) on {video_url}: {comment_text}")
        return True

    except Exception as exc:
        logger.error(f"Comment error on {video_url}: {exc}")
        print_status(f"Comment error: {exc}", "error")
        return False


def run():
    """Main entry point for the comment bot."""
    print_banner()
    print_status("TikTok Comment Bot", "action")
    print_status("=" * 40, "info")

    accounts = load_accounts()
    if not accounts:
        print_status("No accounts available. Run the Account Loader first.", "error")
        return

    video_url = get_target_url()
    total_comments = get_target_count()

    if total_comments > len(accounts):
        print_status(f"Only {len(accounts)} accounts available — capping at that", "warning")
        total_comments = len(accounts)

    use_custom = input(f"\n  Use custom comments? (y/n, default n): ").strip().lower()
    custom_comments = []
    if use_custom == "y":
        print_status("Enter comments (one per line, empty line to finish):", "info")
        while True:
            line = input("    > ").strip()
            if not line:
                break
            custom_comments.append(line)

    comment_pool = custom_comments if custom_comments else config.COMMENT_POOL

    proxies = load_proxies()
    successful = 0
    failed = 0

    print_status(f"\nStarting {total_comments} comments on: {video_url}", "action")
    print_status(f"Comment pool size: {len(comment_pool)}\n", "info")

    for i in range(total_comments):
        account = accounts[i]
        comment_text = random.choice(comment_pool)
        print_status(f"Comment {i + 1}/{total_comments} — {account['username']}", "info")

        proxy = get_random_proxy(proxies)
        driver = None

        try:
            driver = create_browser(proxy)

            if login_account(driver, account["username"], account["password"]):
                if post_comment(driver, video_url, comment_text):
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

        if (i + 1) % config.BATCH_SIZE == 0 and i + 1 < total_comments:
            batch_pause()
        elif i + 1 < total_comments:
            human_delay(2.0)

    print_status("=" * 40, "info")
    print_status(f"Results: {successful} comments, {failed} failed",
                 "success" if successful > 0 else "error")


if __name__ == "__main__":
    run()
