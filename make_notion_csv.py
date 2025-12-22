# make_notion_csv.py

import csv

# ========= Manual Config =========
POSTED_DATE = "18-Dec-25"   # 手动改这里即可
"""
Jan
Feb
Mar
Apr
May
Jun
Jul
Aug
Sep
Oct
Nov
Dec
"""
INPUT_CSV = "download_log_with_drive_links.csv"
OUTPUT_CSV = "notion_version.csv"


def extract_product_from_saved_dir(saved_dir: str) -> str:
    """
    从 saved_dir 里提取 Product 名
    e.g. videos/Cooling Pillowcase/ -> Cooling Pillowcase
    """
    if not saved_dir:
        return ""
    saved_dir = saved_dir.replace("\\", "/").rstrip("/")
    parts = saved_dir.split("/")
    if len(parts) >= 2:
        return parts[-1]
    return ""


def main():
    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_rows = []

    for r in rows:
        video_filename = (r.get("video_filename") or "").strip()
        video_url = (r.get("video_url") or "").strip()
        drive_link = (r.get("drive_link") or "").strip()
        saved_dir = (r.get("saved_dir") or "").strip()

        # 只导出成功且已有 Drive link 的视频
        if not video_filename or not drive_link:
            continue

        out_rows.append({
            "Asset Name": video_filename,
            "Posted Date": POSTED_DATE,
            "Link to Post": video_url,
            "Link to Asset Folder": drive_link,
            "Product": extract_product_from_saved_dir(saved_dir),
        })

    # Sort output rows by Product (primary) then Asset Name (secondary)
    out_rows = sorted(
        out_rows,
        key=lambda r: ((r.get("Product") or "").lower(), (r.get("Asset Name") or "").lower())
    )

    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Asset Name",
                "Posted Date",
                "Link to Post",
                "Link to Asset Folder",
                "Product",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print("========== DONE ==========")
    print(f"Input CSV:   {INPUT_CSV}")
    print(f"Output CSV:  {OUTPUT_CSV}")
    print(f"Posted Date: {POSTED_DATE}")
    print(f"Rows:        {len(out_rows)}")
    print("===========================")


if __name__ == "__main__":
    main()