# main.py
import os
import time
import csv
import re
from downloader import downloadVideo
from browser import get_repost_video_urls
from config import *

# Make sure videos folder exists
os.makedirs("videos", exist_ok=True)

csv_path = CSV_PATH

def ensure_csv_header(path: str):
    """Create CSV with header if not exists."""
    if not os.path.exists(path):
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["author", "video_filename", "video_url", "success_download"])

def parse_author_from_url(url: str) -> str:
    """
    从 TikTok 视频链接里解析作者名（@后面的 username）。
    例: https://www.tiktok.com/@someone/video/123 -> someone
    """
    # CHANGED: 去掉 /video/ 末尾的斜杠，兼容有/无斜杠两种
    m = re.search(r"tiktok\.com/@([^/]+)/video", url)  # CHANGED
    return m.group(1) if m else ""

def main():
    ensure_csv_header(csv_path)

    urlsToDownload = get_repost_video_urls(
        tt_link=TT_LINK,
        max_scrolls=MAX_SCROLLS,
        scroll_pause_time=SCROLL_PAUSE_TIME,
        manual_captcha_seconds=MANUAL_CAPTCHA_SECONDS,
        headless=HEADLESS,
    )

    for index, url in enumerate(urlsToDownload):
        author = parse_author_from_url(url)
        saved_filename = None

        print(f"\n[MAIN INFO]: Downloading video {index + 1}/{len(urlsToDownload)}")
        print(f"[MAIN INFO]: The link of this repost video: {url}")

        try:
            ret = downloadVideo(url, index)
            # CHANGED: 成功需满足 ret 是有效路径且文件真实存在
            if isinstance(ret, str) and ret.strip() and os.path.exists(ret):  # CHANGED
                saved_filename = os.path.basename(ret)  # CHANGED
                success = True                          # CHANGED
            else:
                success = False                         # CHANGED
        except Exception as e:
            print(f"[MAIN INFO]: ❌ Failed to download video {index}: {e}")
            success = False
            # 失败时也会写入 CSV，方便后续排查

        # --- 实时写 CSV（逐条 append） ---
        with open(csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([author, saved_filename or "", url, "yes" if success else "no"])  # CHANGED（用真实文件名或空）
            f.flush()  # 立刻落盘，确保实时可见

        time.sleep(10)  # 降低被风控概率

if __name__ == "__main__":
    main()

