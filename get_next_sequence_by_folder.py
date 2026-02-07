import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ========= 配置 =========
SERVICE_ACCOUNT_FILE = "service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# ✅ 你可以填 folder link 或 folder id
ROOT_FOLDER = "https://drive.google.com/drive/folders/1SKhKRcwTm6lvDcw-ZCUFNxcDXLNdqS_0"
# ROOT_FOLDER = "1SKhKRcwTm6lvDcw-ZCUFNxcDXLNdqS_0"

# =======================

def parse_folder_id(s: str) -> str:
    s = s.strip()
    # 1) 直接是 id
    if re.fullmatch(r"[A-Za-z0-9_-]{10,}", s) and "drive.google.com" not in s:
        return s
    # 2) URL 里抽取 /folders/<id>
    m = re.search(r"/folders/([A-Za-z0-9_-]+)", s)
    if m:
        return m.group(1)
    # 3) open?id=<id>
    m = re.search(r"[?&]id=([A-Za-z0-9_-]+)", s)
    if m:
        return m.group(1)
    raise ValueError(f"Cannot parse folder id from: {s}")

def get_drive_service():
    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)

def list_folders(service, parent_id):
    results = service.files().list(
        q=(
            f"'{parent_id}' in parents "
            "and mimeType='application/vnd.google-apps.folder' "
            "and trashed=false"
        ),
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])

def list_files(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="files(name)"
    ).execute()
    return results.get("files", [])

def extract_sequence(filename):
    # 只匹配： 123_xxx.mp4
    match = re.match(r"^(\d+)_", filename)
    return int(match.group(1)) if match else None

def get_next_sequence_map(root_folder_id):
    service = get_drive_service()

    # ✅ 先验证 root folder 本身存在（能更早暴露权限问题）
    service.files().get(fileId=root_folder_id, fields="id,name").execute()

    output = {}
    folders = list_folders(service, root_folder_id)

    for folder in folders:
        folder_name = folder["name"]
        folder_id = folder["id"]

        max_seq = 0
        files = list_files(service, folder_id)

        for f in files:
            seq = extract_sequence(f["name"])
            if seq is not None:
                max_seq = max(max_seq, seq)

        output[folder_name] = max_seq + 1 if max_seq > 0 else 1

    return output

if __name__ == "__main__":
    root_id = parse_folder_id(ROOT_FOLDER)
    result = get_next_sequence_map(root_id)

    print()
    for k, v in result.items():
        print(f'    "{k}": {v},')
    print()

