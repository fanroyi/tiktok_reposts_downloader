# main.py
import os
import time
import csv
import shutil

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
    preflight_preview,
    normalize_author,
    sanitize_fs_name,
    product_to_folder,
    product_to_token,
    get_next_index_for_dir,
)

# Ensure base folders exist
os.makedirs("videos", exist_ok=True)
os.makedirs(os.path.join("videos", "wl"), exist_ok=True)
os.makedirs(os.path.join("videos", "unknown"), exist_ok=True)


def ensure_csv_header(path: str):
    """Ensure CSV header matches required export format."""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "creator",
                "video_url",
                "stdads_filename",
                "stdads_saved_dir",
                "wlads_filename",
                "wlads_saved_dir",
                "stdads_success",
                "wl_copy_success",
                "error",
            ])


def get_available_filepath(dir_path: str, base_name: str, ext: str = ".mp4") -> str:
    """Avoid overwrite: auto append -1, -2..."""
    os.makedirs(dir_path, exist_ok=True)
    candidate = os.path.join(dir_path, f"{base_name}{ext}")
    if not os.path.exists(candidate):
        return candidate

    counter = 1
    while True:
        candidate = os.path.join(dir_path, f"{base_name}-{counter}{ext}")
        if not os.path.exists(candidate):
            return candidate
        counter += 1


def main():
    ensure_csv_header(CSV_PATH)

    wl_authors = load_wl_authors(WL_LIST_CSV)
    rows = load_rows(INPUT_CSV_PATH)

    # Preflight preview + ENTER to continue
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
            # 1) StdAds (ALL videos)
            # =========================
            if product_folder == "unknown":
                stdads_dir = os.path.join("videos", "unknown")
                os.makedirs(stdads_dir, exist_ok=True)

                stdads_base = f"{creator_handle}_StdAds_{product_token}"
            else:
                stdads_dir = os.path.join("videos", product_folder)
                os.makedirs(stdads_dir, exist_ok=True)

                start_num = START_NUM_BY_FOLDER.get(product_folder, UNKNOWN_START_NUM)
                next_idx = get_next_index_for_dir(stdads_dir, start=start_num)
                stdads_base = f"{next_idx}_{creator_handle}_StdAds_{product_token}"

            print(f"\n[MAIN INFO]: Downloading {idx + 1}/{len(rows)}")
            print(f"[MAIN INFO]: StdAds → {stdads_dir}/{stdads_base}.mp4")

            stdads_success = False
            wl_copy_success = False
            stdads_filename = ""
            wlads_filename = ""
            wlads_dir = ""
            err = ""
            ret = None

            try:
                ret = downloadVideo(
                    link=url,
                    id=idx,
                    save_dir=stdads_dir,
                    filename_base=stdads_base,
                )
                stdads_success = bool(ret and os.path.exists(ret))
                if stdads_success:
                    stdads_filename = os.path.basename(ret)
            except Exception as e:
                err = str(e)

            # =========================
            # 2) WL copy (if applicable)
            # =========================
            if is_wl and stdads_success:
                wlads_dir = os.path.join("videos", "wl", creator_safe)
                os.makedirs(wlads_dir, exist_ok=True)

                wlads_base = f"{creator_handle}_WLAds_{product_token}"
                wl_dst_path = get_available_filepath(wlads_dir, wlads_base)

                try:
                    shutil.copy2(ret, wl_dst_path)
                    wl_copy_success = True
                    wlads_filename = os.path.basename(wl_dst_path)
                    print(f"[MAIN INFO]: WL copy → {wl_dst_path}")
                except Exception as e:
                    wl_copy_success = False
                    err = (err + " | " if err else "") + f"WL copy failed: {e}"

            # =========================
            # 3) Export CSV row
            # =========================
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    creator_raw,
                    url,
                    stdads_filename,
                    stdads_dir,
                    wlads_filename,
                    wlads_dir,
                    "yes" if stdads_success else "no",
                    "yes" if wl_copy_success else "no",
                    err,
                ])
                f.flush()

            time.sleep(SLEEP_SECONDS)

    except KeyboardInterrupt:
        print("\n[MAIN INFO]: ⛔ Ctrl+C detected, exiting safely")


if __name__ == "__main__":
    main()
