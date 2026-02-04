# config_drive.py

# ========= Google Drive Auth =========
# Service Account key 文件路径
SERVICE_ACCOUNT_JSON = "service_account.json"

# ========= Google Drive Folder =========
# 你给我的 Google Drive 文件夹「链接 或 folder_id」
# 例如：
#   https://drive.google.com/drive/folders/1AbCdEfGhIjKlMn
# 或：
#   1AbCdEfGhIjKlMn
DRIVE_ROOT = "https://drive.google.com/drive/folders/1SKhKRcwTm6lvDcw-ZCUFNxcDXLNdqS_0"

# ========= CSV =========
INPUT_CSV = "download_log.csv"
OUTPUT_CSV = "download_log_with_drive_links.csv"

# 是否直接覆盖 INPUT_CSV（谨慎）
INPLACE = False

# ========= Matching Rules =========
# 只给 success = yes 的行填 link（强烈推荐 True）
ONLY_SUCCESS_YES = True

# 允许的视频文件扩展名
VIDEO_EXTENSIONS = (
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".webm",
)
