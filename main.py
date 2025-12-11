import os
import time
import csv
import re

from downloader import downloadVideo
from browser import get_repost_video_urls
from config import *  # expects: CSV_PATH, TT_LINK, MAX_SCROLLS, SCROLL_PAUSE_TIME, MANUAL_CAPTCHA_SECONDS, HEADLESS, WL_LIST_CSV

# Make sure videos & WL folder exist
os.makedirs("videos", exist_ok=True)
os.makedirs(os.path.join("videos", "WL"), exist_ok=True)

csv_path = CSV_PATH


def ensure_csv_header(path: str):
    """Create CSV with header if not exists."""
    if not os.path.exists(path):
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "author",
                "video_filename",
                "video_url",
                "success_download",
                "exists_in_folder",
            ])


def parse_author_from_url(url: str) -> str:
    """
    从 TikTok 视频链接里解析作者名（@后面的 username）。
    例: https://www.tiktok.com/@someone/video/123 -> someone
    """
    m = re.search(r"tiktok\.com/@([^/]+)/video", url)
    return m.group(1) if m else ""


def normalize_author(name: str) -> str:
    """
    统一作者名格式：去空格、逗号、前导 @，转小写。
    用于和 WL 列表匹配。
    """
    if not name:
        return ""
    name = name.strip().strip(",").lstrip("@")
    return name.lower()


def load_wl_authors(csv_file: str):
    """
    读取白名单作者列表 CSV（只有一列，author 名称）。
    返回归一化后的 set 方便快速判断。
    """
    authors = set()
    if os.path.exists(csv_file):
        with open(csv_file, "r", encoding="utf-8") as f:
            for line in f:
                norm = normalize_author(line)
                if norm:
                    authors.add(norm)
        print(f"[MAIN INFO]: Loaded {len(authors)} WL authors from {csv_file}")
    else:
        print(f"[MAIN WARN]: WL list CSV not found: {csv_file}")
    return authors


def get_base_author_from_filename(filename: str) -> str:
    """
    根据文件名推断作者名（不含扩展名）：
    - 输入示例：
        roy.mp4, roy-1.mp4, roy-2.mp4,
        roy-y.mp4, roy-y-1.mp4
    - 规则：
        1. 去掉扩展名，得到 base，如 'roy-1'、'roy-y-1'
        2. 从右往左按 '-' 拆一刀：
            - 如果右边是纯数字，则去掉这一段，剩下的是作者名
              例：'roy-1' -> 'roy'； 'roy-y-2' -> 'roy-y'
            - 否则，整个 base 就是作者名
              例：'roy-y' -> 'roy-y'
    """
    base, _ = os.path.splitext(filename)  # 'roy-1' / 'roy-y-1'
    parts = base.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        author_part = parts[0]
    else:
        author_part = base
    return normalize_author(author_part)


def move_wl_videos_after_download(wl_authors_norm: set):
    """
    在“当前已经下载完成”的基础上，扫描 videos/ 目录，
    把白名单作者的视频移动到 videos/WL/。

    - 只遍历 videos/ 根目录下的文件（跳过子目录，比如 WL）。
    - 对每个文件名做 base-author 解析，再归一化后在 wl_authors_norm 里查。
    - 匹配成功则移动到 videos/WL/ 下，文件名保持不变。
    """
    videos_root = "videos"
    wl_root = os.path.join("videos", "WL")

    moved_count = 0

    for fname in os.listdir(videos_root):
        src_path = os.path.join(videos_root, fname)

        # 跳过子目录（例如 WL）
        if os.path.isdir(src_path):
            continue

        # 只处理常见视频后缀
        if not fname.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
            continue

        base_author_norm = get_base_author_from_filename(fname)

        if base_author_norm in wl_authors_norm:
            dst_path = os.path.join(wl_root, fname)
            try:
                os.replace(src_path, dst_path)
                moved_count += 1
                print(f"[MAIN INFO]: ➡️ Moved WL video: {fname} -> {dst_path}")
            except Exception as e:
                print(f"[MAIN ERROR]: ❌ Failed moving WL video {fname}: {e}")

    print(f"[MAIN INFO]: Finished moving WL videos. Total moved: {moved_count}")


def main():
    # 确保 CSV 有表头
    ensure_csv_header(csv_path)

    # 一开始就加载 WL 列表，这样即使中途 Ctrl+C，也能用这个列表去移动已下载的视频
    wl_authors_norm = load_wl_authors(WL_LIST_CSV)

    try:
        # 获取需要下载的 Repost 视频链接
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
            print(f"[MAIN INFO]: Parsed author: {author}")

            try:
                ret = downloadVideo(url, index)

                # 成功需满足 ret 是有效路径且文件真实存在
                if isinstance(ret, str) and ret.strip() and os.path.exists(ret):
                    saved_filename = os.path.basename(ret)
                    success = True
                else:
                    success = False

            except Exception as e:
                print(f"[MAIN INFO]: ❌ Failed to download video {index}: {e}")
                success = False

            # 下载结束时，文件此时应该还在 videos/ 根目录
            if saved_filename:
                full_path = os.path.join("videos", saved_filename)
                exists_in_folder = "yes" if os.path.exists(full_path) else "no"
            else:
                exists_in_folder = "no"

            # --- 实时写 CSV（逐条 append） ---
            with open(csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    author,
                    saved_filename or "",
                    url,
                    "yes" if success else "no",
                    exists_in_folder,
                ])
                f.flush()  # 立刻落盘

            # 降低被风控概率
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n[MAIN INFO]: ⛔ Detected Ctrl+C, stopping downloads early...")
    finally:
        # 不管正常结束还是 Ctrl+C，都会尝试把当前已经下载的 WL 视频挪到 WL 目录
        if wl_authors_norm:
            print("[MAIN INFO]: Now moving WL videos based on current downloads...")
            move_wl_videos_after_download(wl_authors_norm)
        else:
            print("[MAIN INFO]: No WL authors loaded, skip moving WL videos.")


if __name__ == "__main__":
    main()
