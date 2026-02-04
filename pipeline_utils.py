# pipeline_utils.py
import os
import csv
import re

from config import PRODUCT_SUBFOLDER_MAP


def ensure_csv_header(path: str):
    if not os.path.exists(path):
        with open(path, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow([
                "creator",
                "video_filename",
                "video_url",
                "product_folder",
                "is_wl",
                "saved_dir",
                "success_download",
                "error",
            ])


def normalize_author(name: str) -> str:
    if not name:
        return ""
    return name.strip().strip(",").lstrip("@").lower()


def sanitize_fs_name(name: str, max_len: int = 140) -> str:
    if not name:
        return ""
    name = name.strip()
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = re.sub(r"[\r\n\t]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:max_len]


def product_to_folder(product_value: str) -> str:
    """
    Decide the StdAds product folder name.

    Priority:
    1) If product_value contains any key in PRODUCT_SUBFOLDER_MAP, use mapped subfolder name.
    2) Otherwise use default parsing: take text after '|' if exists, sanitize and truncate.
    """
    if not product_value:
        return "unknown"

    raw = product_value.strip()

    # 1) override map (contains match)
    for k, v in PRODUCT_SUBFOLDER_MAP.items():
        if k and k in raw:
            return v

    # 2) default behavior
    txt = raw
    if "|" in txt:
        txt = txt.split("|", 1)[1].strip()
    txt = sanitize_fs_name(txt, max_len=160)
    return txt or "unknown"


def product_to_token(product_value: str) -> str:
    """
    Product token used in filename.

    Priority:
    1) If PRODUCT_SUBFOLDER_MAP matches → use subfolder name as token
    2) Otherwise fallback to parsed short token from raw product text
    """
    if not product_value:
        return "UnknownProduct"

    raw = product_value.strip()

    # ✅ 1) If mapped to a subfolder, reuse it as token
    for k, v in PRODUCT_SUBFOLDER_MAP.items():
        if k and k in raw:
            # Turn "Cooling Blanket" → "CoolingBlanket"
            return re.sub(r"\s+", "", v)

    # 2) fallback (original behavior)
    txt = raw
    if "|" in txt:
        txt = txt.split("|", 1)[1].strip()

    txt = re.sub(r"[^A-Za-z0-9 ]+", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()

    words = txt.split(" ")[:4]
    return "".join(w.capitalize() for w in words) or "UnknownProduct"



def load_wl_authors(path: str) -> set:
    s = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                v = normalize_author(line)
                if v:
                    s.add(v)
        print(f"[MAIN INFO]: Loaded {len(s)} WL authors")
    else:
        print(f"[MAIN WARN]: WL list not found, WL disabled")
    return s


def load_ai_authors(path: str) -> set:
    """
    AI list 格式和 WL 一样：一行一个 creator（可带@）
    命中后：main 里会 skip（不下载、不写 download_log）
    """
    s = set()
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                v = normalize_author(line)
                if v:
                    s.add(v)
        print(f"[MAIN INFO]: Loaded {len(s)} AI authors")
    else:
        print(f"[MAIN WARN]: AI list not found, AI skip disabled")
    return s


def detect_delimiter(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig") as f:
        sample = f.read(4096)
    if sample.count("\t") >= max(3, sample.count(",")):
        return "\t"
    return ","


def load_rows(path: str):
    delim = detect_delimiter(path)

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=delim)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")

        url_k = creator_k = product_k = None
        for k in reader.fieldnames:
            lk = k.lower()
            if lk in ("url", "video_url", "tiktok_url", "link"):
                url_k = k
            elif lk in ("creator", "author", "username"):
                creator_k = k
            elif lk in ("product", "product_name"):
                product_k = k

        if not url_k or not creator_k or not product_k:
            raise ValueError(f"Missing required columns: {reader.fieldnames}")

        rows = []
        for r in reader:
            url = (r.get(url_k) or "").strip()
            if url and "tiktok.com" in url and "/video/" in url:
                rows.append({
                    "url": url,
                    "creator": (r.get(creator_k) or "").strip(),
                    "product": (r.get(product_k) or "").strip(),
                })

    print(f"[MAIN INFO]: Loaded {len(rows)} rows from CSV")
    return rows


def get_next_index_for_dir(dir_path: str, start: int) -> int:
    max_seen = None
    if os.path.exists(dir_path):
        for fn in os.listdir(dir_path):
            m = re.match(r"^(\d+)_", fn)
            if m:
                n = int(m.group(1))
                max_seen = n if max_seen is None or n > max_seen else max_seen
    return start if max_seen is None else max_seen + 1


def preview_product_folder_mapping(rows: list):
    """
    Print unique RAW product names and their resulting subfolder names
    BEFORE downloading, so you can decide overrides in config.py.
    """
    seen = {}
    for row in rows:
        raw = (row.get("product") or "").strip()
        if not raw:
            continue
        if raw not in seen:
            seen[raw] = product_to_folder(raw)

    if not seen:
        return

    print("\n========== PRODUCT → SUBFOLDER PREVIEW ==========")
    for idx, (raw, folder) in enumerate(seen.items(), 1):
        print(f"[{idx}]")
        print("RAW PRODUCT:")
        print(raw)
        print("\n→ CURRENT SUBFOLDER:")
        print(folder)
        print("\n" + "-" * 56)
    print("===============================================\n")


def preflight_preview(rows: list, wl_authors: set, start_num_by_folder: dict, unknown_start_num: int):
    stdads_product_dirs = set()
    wl_creator_dirs = set()
    missing = set()
    unknown_count = 0

    for row in rows:
        creator_raw = row["creator"]
        product_raw = row["product"]

        creator_match = normalize_author(creator_raw)
        creator_safe = sanitize_fs_name(creator_raw) or "unknown"

        product_folder = product_to_folder(product_raw)
        if product_folder == "unknown":
            unknown_count += 1

        is_wl = creator_match in wl_authors

        if is_wl:
            wl_creator_dirs.add(os.path.join("videos", "wl", creator_safe))
        else:
            stdads_product_dirs.add(os.path.join("videos", product_folder))
            if product_folder not in start_num_by_folder and product_folder != "unknown":
                missing.add(product_folder)

    print("\n========== PREFLIGHT PREVIEW ==========")
    print(f"Input rows: {len(rows)}")
    print(f"WL authors loaded: {len(wl_authors)}")
    if unknown_count:
        print(f"⚠️ Rows with empty/unknown product: {unknown_count} (folder: videos/unknown/)")

    print("\n[StdAds] Product folders that will be created/used:")
    for p in sorted(stdads_product_dirs):
        folder_name = os.path.basename(p.rstrip("/"))
        start_num = start_num_by_folder.get(folder_name, unknown_start_num)
        tag = "config" if folder_name in start_num_by_folder else "⚠️ default"
        print(f"  - {p}  | start={start_num}  ({tag})")

    print("\n[WLAds] Creator folders that will be created/used:")
    for p in sorted(wl_creator_dirs):
        print(f"  - {p}")

    if missing:
        print("\n⚠️ Missing in START_NUM_BY_FOLDER (StdAds will default to UNKNOWN_START_NUM):")
        for m in sorted(missing):
            print(f"  - {m}")
        print("Tip: add them into config.py START_NUM_BY_FOLDER if you want custom start numbers.")

    print("======================================\n")

    user_in = input("Press ENTER to start downloading, or type 'q' to quit: ").strip().lower()
    if user_in == "q":
        print("[MAIN INFO]: Quit by user. No downloads started.")
        return False
    return True
