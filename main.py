# main.py
import os
import time
import csv

from downloader import downloadVideo
from config import (
    INPUT_CSV_PATH,
    CSV_PATH,
    WL_LIST_CSV,
    AI_LIST_CSV,
    SLEEP_SECONDS,
    START_NUM_BY_FOLDER,
    UNKNOWN_START_NUM,
)

from pipeline_utils import (
    load_wl_authors,
    load_ai_authors,
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
    ai_authors = load_ai_authors(AI_LIST_CSV)
    rows = load_rows(INPUT_CSV_PATH)

    # Preview product → folder mapping
    preview_product_folder_mapping(rows)

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

            # ===== AI SKIP =====
            if creator_match in ai_authors:
                print(f"\n[SKIP AI]: {creator_handle} | {url}")
                continue

            product_folder = product_to_folder(product_raw)
            product_token = product_to_token(product_raw)
            is_wl = creator_match in wl_authors

            err = ""
            success = False
            video_filename = ""
            saved_dir = ""
            filename_base = ""

            # =========================
            # WL Ads
            # =========================
            if is_wl:
                saved_dir = os.path.join("videos", "wl", creator_safe)
                os.makedirs(saved_dir, exist_ok=True)

                filename_base = f"{creator_handle}_{product_token}_WLAds"

                print(f"\n[MAIN INFO]: Downloading {idx + 1}/{len(rows)} (WL)")
                print(f"[MAIN INFO]: WL → {saved_dir}/{filename_base}.mp4")

            # =========================
            # Std Ads
            # =========================
            else:
                if product_folder == "unknown":
                    saved_dir = os.path.join("videos", "unknown")
                    os.makedirs(saved_dir, exist_ok=True)

                    # unknown 不编号
                    filename_base = f"{creator_handle}_{product_token}_StdAds"

                else:
                    saved_dir = os.path.join("videos", product_folder)
                    os.makedirs(saved_dir, exist_ok=True)

                    start_num = START_NUM_BY_FOLDER.get(
                        product_folder, UNKNOWN_START_NUM
                    )
                    next_idx = get_next_index_for_dir(saved_dir, start=start_num)

                    # ✅ 关键改动：编号放最前面
                    filename_base = f"{next_idx}_{creator_handle}_{product_token}_StdAds"

                print(f"\n[MAIN INFO]: Downloading {idx + 1}/{len(rows)} (StdAds)")
                print(f"[MAIN INFO]: StdAds → {saved_dir}/{filename_base}.mp4")

            # =========================
            # Download
            # =========================
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
            # CSV log
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
