from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict, List

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config_drive as cfg


SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


# =========================
# Utils
# =========================
def drive_folder_id_from_link(link_or_id: str) -> str:
    s = (link_or_id or "").strip()
    if "/folders/" in s:
        s = s.split("/folders/", 1)[1]
        s = s.split("?", 1)[0]
        s = s.split("/", 1)[0]
    return s


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        cfg.SERVICE_ACCOUNT_JSON,
        scopes=SCOPES,
    )
    return build(
        "drive",
        "v3",
        credentials=creds,
        cache_discovery=False,  # 避免一些奇怪的卡顿
    )


# =========================
# Drive helpers
# =========================
@dataclass
class DriveNode:
    id: str
    name: str
    mimeType: str
    webViewLink: str


def list_children(service, folder_id: str) -> List[DriveNode]:
    """
    List children of a folder.
    IMPORTANT: webViewLink is fetched here to avoid per-file files().get()
    """
    out: List[DriveNode] = []
    page_token = None

    while True:
        res = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id,name,mimeType,webViewLink)",
            pageSize=1000,
            pageToken=page_token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True,
            corpora="allDrives",
        ).execute()

        for f in res.get("files", []):
            out.append(
                DriveNode(
                    id=f["id"],
                    name=f.get("name", ""),
                    mimeType=f.get("mimeType", ""),
                    webViewLink=f.get("webViewLink", "") or "",
                )
            )

        page_token = res.get("nextPageToken")
        if not page_token:
            break

    return out


def build_drive_filename_map(service, root_folder_id: str) -> Dict[str, str]:
    """
    Build mapping:
        filename -> webViewLink
    """
    mapping: Dict[str, str] = {}
    duplicates = 0
    scanned_files = 0
    scanned_folders = 0

    stack = [root_folder_id]

    print(f"[INFO] Scanning Drive folder: {root_folder_id}", flush=True)

    while stack:
        fid = stack.pop()
        scanned_folders += 1

        try:
            children = list_children(service, fid)
        except HttpError as e:
            print(f"[WARN] Failed listing folder {fid}: {e}", flush=True)
            continue

        for node in children:
            if node.mimeType == "application/vnd.google-apps.folder":
                stack.append(node.id)
                continue

            scanned_files += 1

            lower = node.name.lower()
            if not any(lower.endswith(ext) for ext in cfg.VIDEO_EXTENSIONS):
                continue

            if not node.webViewLink:
                continue

            if node.name in mapping and mapping[node.name] != node.webViewLink:
                duplicates += 1
                print(f"[WARN] Duplicate filename on Drive: {node.name}", flush=True)
                continue

            mapping[node.name] = node.webViewLink

            if scanned_files % 200 == 0:
                print(
                    f"[INFO] scanned folders={scanned_folders}, files={scanned_files}, mapped={len(mapping)}",
                    flush=True,
                )

    print(f"[INFO] Drive scan done")
    print(f"[INFO] Total folders scanned: {scanned_folders}")
    print(f"[INFO] Total video files indexed: {len(mapping)}")
    if duplicates:
        print(f"[INFO] Duplicate filename warnings: {duplicates}")

    return mapping


# =========================
# CSV update
# =========================
def update_csv_with_drive_links(drive_map: Dict[str, str]):
    with open(cfg.INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if "drive_link" not in fieldnames:
        fieldnames.append("drive_link")

    filled = missing = skipped = 0

    for r in rows:
        fn = (r.get("video_filename") or "").strip()
        success = (r.get("success") or "").strip().lower()

        if cfg.ONLY_SUCCESS_YES and success not in ("yes", "y", "true", "1"):
            skipped += 1
            continue

        if not fn:
            skipped += 1
            continue

        if (r.get("drive_link") or "").strip():
            continue

        link = drive_map.get(fn, "")
        if link:
            r["drive_link"] = link
            filled += 1
        else:
            missing += 1

    out_path = cfg.INPUT_CSV if cfg.INPLACE else cfg.OUTPUT_CSV
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[DONE] Wrote: {out_path}")
    print(f"[INFO] Links filled: {filled}")
    print(f"[INFO] Missing (success=yes but not found on Drive): {missing}")
    print(f"[INFO] Skipped rows: {skipped}")


# =========================
# Main
# =========================
def main():
    root_id = drive_folder_id_from_link(cfg.DRIVE_ROOT)
    service = get_drive_service()
    drive_map = build_drive_filename_map(service, root_id)
    update_csv_with_drive_links(drive_map)


if __name__ == "__main__":
    main()
