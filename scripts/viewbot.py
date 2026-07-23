"""
viewbot.py — TikTok view bot.
Opens target video URLs across multiple browser sessions with
randomized watch durations to inflate view counts.
"""

import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium.webdriver.common.by import By

from . import config
from .utils import (
    setup_logger, print_banner, print_status,
    load_proxies, get_random_proxy, create_browser,
    human_delay, batch_pause, wait_for_element,
    safe_quit, get_target_url, get_target_count
)

logger = setup_logger("view-bot")

view_lock = threading.Lock()
views_completed = 0


def watch_video(video_url: str, proxy: str | None = None, view_number: int = 0) -> bool:
    """
    Open a TikTok video and watch it for a randomized duration.
    *TikTok counts a view after ~3s of watch time — we exceed that minimum
     with jitter to appear organic.*
    """
    global views_completed
    driver = None

    try:
        driver = create_browser(proxy)
        driver.get(video_url)
        human_delay(1.5)

        video_element = wait_for_element(
            driver, By.TAG_NAME, "video", timeout=15
        )

        if not video_element:
            video_element = wait_for_element(
                driver, By.XPATH,
                "//div[contains(@class, 'video-player')]//video | //div[@data-e2e='browse-video']//video",
                timeout=10
            )

        if video_element:
            try:
                driver.execute_script("""
                    var video = arguments[0];
                    if (video.paused) { video.play(); }
                    video.muted = true;
                """, video_element)
            except Exception:
                pass

            watch_time = random.uniform(
                config.VIEW_DURATION_MIN,
                config.VIEW_DURATION_MAX
            )
            print_status(f"View #{view_number} — watching for {watch_time:.1f}s", "action")
            time.sleep(watch_time)

            if random.random() > 0.6:
                driver.execute_script("window.scrollBy(0, arguments[0]);",
                                      random.randint(50, 200))
                time.sleep(random.uniform(0.5, 1.5))

            with view_lock:
                views_completed += 1

            print_status(f"View #{view_number} complete", "success")
            logger.info(f"View #{view_number} completed on {video_url}")
            return True

        else:
            print_status(f"View #{view_number} — video element not found", "warning")
            logger.warning(f"Video element not found for view #{view_number}")
            return False

    except Exception as exc:
        print_status(f"View #{view_number} failed: {exc}", "error")
        logger.error(f"View #{view_number} error: {exc}")
        return False

    finally:
        safe_quit(driver)


def run():
    """Main entry point for the view bot."""
    global views_completed
    views_completed = 0

    print_banner()
    print_status("TikTok View Bot", "action")
    print_status("=" * 40, "info")

    video_url = get_target_url()
    total_views = get_target_count()

    try:
        max_threads = int(input(f"  Max concurrent browsers (default 3): ").strip() or "3")
        max_threads = max(1, min(max_threads, 10))
    except ValueError:
        max_threads = 3

    proxies = load_proxies()
    successful = 0
    failed = 0

    print_status(f"\nStarting {total_views} views on: {video_url}", "action")
    print_status(f"Concurrent browsers: {max_threads}\n", "info")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []

        for i in range(total_views):
            proxy = get_random_proxy(proxies)
            future = executor.submit(watch_video, video_url, proxy, i + 1)
            futures.append(future)

            time.sleep(random.uniform(0.5, 1.5))

            if (i + 1) % config.BATCH_SIZE == 0 and i + 1 < total_views:
                print_status(f"Batch {(i + 1) // config.BATCH_SIZE} complete — pausing...", "info")
                batch_pause()

        for future in as_completed(futures):
            if future.result():
                successful += 1
            else:
                failed += 1

    print_status("=" * 40, "info")
    print_status(f"Results: {successful} views sent, {failed} failed", "success" if successful > 0 else "error")


if __name__ == "__main__":
    run()
