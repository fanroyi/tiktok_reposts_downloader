# main.py
import os
import time
import csv

from downloader import downloadVideo
from config import (
    INPUT_CSV_PATH,
    CSV_PATH,
    WL_LIST_CSV,
    SLEEP_SECONDS,
    START_NUM_BY_FOLDER,
    UNKNOWN_START_NUM,
)

from pipeline_utils import (
    load_wl_authors,
    load_rows,
    preview_product_folder_mapping,
    normalize_author,
    sanitize_fs_name,
    product_to_folder,
    product_to_token,
    get_next_index_for_dir,
    preflight_preview,
)

# Ensure base folders exist
os.makedirs("videos", exist_ok=True)
os.makedirs(os.path.join("videos", "wl"), exist_ok=True)
os.makedirs(os.path.join("videos", "unknown"), exist_ok=True)


def ensure_csv_header(path: str):
    """
    New unified CSV format:
    - WL videos only stored under videos/wl/<creator>/
    - StdAds videos stored under videos/<product_folder>/ or videos/unknown/
    """
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "creator",
                "video_url",
                "is_wl",
                "product_folder",
                "video_filename",
                "saved_dir",
                "success",
                "error",
            ])


def main():
    ensure_csv_header(CSV_PATH)

    wl_authors = load_wl_authors(WL_LIST_CSV)
    rows = load_rows(INPUT_CSV_PATH)

    # 先打印 RAW product → folder 预览（方便你做 override）
    preview_product_folder_mapping(rows)

    # 仍然保留你原来的 preflight（编号检查、目录预览）
    if not preflight_preview(
        rows=rows,
        wl_authors=wl_authors,
        start_num_by_folder=START_NUM_BY_FOLDER,
        unknown_start_num=UNKNOWN_START_NUM,
    ):
        return

    try:
        for idx, row in enumerate(rows):
            url = row["url"]
            creator_raw = row["creator"]
            product_raw = row["product"]

            creator_match = normalize_author(creator_raw)
            creator_safe = sanitize_fs_name(creator_raw) or "unknown"
            creator_handle = f"@{creator_match or creator_safe}"

            product_folder = product_to_folder(product_raw)
            product_token = product_to_token(product_raw)

            is_wl = creator_match in wl_authors

            # =========================
            # Decide ONLY ONE destination:
            # - WL: videos/wl/<creator_safe>/
            # - StdAds: videos/<product_folder>/ or videos/unknown/
            # =========================
            err = ""
            success = False
            video_filename = ""
            saved_dir = ""
            filename_base = ""

            if is_wl:
                saved_dir = os.path.join("videos", "wl", creator_safe)
                os.makedirs(saved_dir, exist_ok=True)

                # WL 命名：不需要编号（你也可以想要编号的话我再给你加）
                filename_base = f"{creator_handle}_WLAds_{product_token}"
                print(f"\n[MAIN INFO]: Downloading {idx + 1}/{len(rows)} (WL)")
                print(f"[MAIN INFO]: WL → {saved_dir}/{filename_base}.mp4")
            else:
                if product_folder == "unknown":
                    saved_dir = os.path.join("videos", "unknown")
                    os.makedirs(saved_dir, exist_ok=True)
                    filename_base = f"{creator_handle}_StdAds_{product_token}"
                else:
                    saved_dir = os.path.join("videos", product_folder)
                    os.makedirs(saved_dir, exist_ok=True)

                    start_num = START_NUM_BY_FOLDER.get(product_folder, UNKNOWN_START_NUM)
                    next_idx = get_next_index_for_dir(saved_dir, start=start_num)
                    filename_base = f"{next_idx}_{creator_handle}_StdAds_{product_token}"

                print(f"\n[MAIN INFO]: Downloading {idx + 1}/{len(rows)} (StdAds)")
                print(f"[MAIN INFO]: StdAds → {saved_dir}/{filename_base}.mp4")

            # =========================
            # Download (ONLY ONCE)
            # =========================
            ret = None
            try:
                ret = downloadVideo(
                    link=url,
                    id=idx,
                    save_dir=saved_dir,
                    filename_base=filename_base,
                )
                success = bool(ret and os.path.exists(ret))
                if success:
                    video_filename = os.path.basename(ret)
            except Exception as e:
                err = str(e)

            # =========================
            # Export CSV row (single set of columns)
            # =========================
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    creator_raw,
                    url,
                    "yes" if is_wl else "no",
                    product_folder,
                    video_filename,
                    saved_dir,
                    "yes" if success else "no",
                    err,
                ])
                f.flush()

            time.sleep(SLEEP_SECONDS)

    except KeyboardInterrupt:
        print("\n[MAIN INFO]: ⛔ Ctrl+C detected, exiting safely")


if __name__ == "__main__":
    main()
