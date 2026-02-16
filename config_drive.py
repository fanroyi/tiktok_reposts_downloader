# config_drive.py

# ========= Google Drive Auth =========
# Path to your Service Account key file
SERVICE_ACCOUNT_JSON = "service_account.json"

# ========= Google Drive Folder =========
# Your Google Drive folder link or folder_id
# For example:
#   https://drive.google.com/drive/folders/1AbCdEfGhIjKlMn
# or:
#   1AbCdEfGhIjKlMn
DRIVE_ROOT = "https://drive.google.com/drive/folders/1SKhKRcwTm6lvDcw-ZCUFNxcDXLNdqS_0"

# ========= CSV =========
INPUT_CSV = "download_log.csv"
OUTPUT_CSV = "download_log_with_drive_links.csv"

# Whether to overwrite INPUT_CSV directly (use with caution)
INPLACE = False

# ========= Matching Rules =========
# Only populate link for rows where success = "yes"
# (strongly recommended to keep this True)
ONLY_SUCCESS_YES = True

# Allowed video file extensions
VIDEO_EXTENSIONS = (
    ".mp4",
    ".mov",
    ".m4v",
    ".mkv",
    ".webm",
)
