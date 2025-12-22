# TikTok Reposts Downloader

This project scrapes reposted TikTok video URLs from a profile, downloads no‑watermark video files via ssstik.io, logs download metadata, and retrieves file links from a Google Drive folder using a Google Service Account.

## Google Drive (required)

This project requires a Google Service Account which must be granted access to the Drive folder the script will read/write. Complete these steps before running the tool.

1. Create a Google Cloud Project  
   - Visit: https://console.cloud.google.com/ and create/select a project.

2. Enable Google Drive API  
   - APIs & Services → Library → search "Google Drive API" → Enable.

3. Create a Service Account  
   - IAM & Admin → Service Accounts → Create Service Account  
   - Example name: `drive-link-bot`  
   - Skip role assignment.

4. Generate `service_account.json`  
   - Open the service account → Keys → Add Key → Create new key → JSON  
   - Download and rename to `service_account.json`  
   - Place it in the project root.  
   - DO NOT commit this file. Add to `.gitignore`:
     ```
     service_account.json
     ```

5. Share your Drive folder with the Service Account (critical)  
   - In Google Drive, right-click the folder → Share  
   - Add the service account email (looks like `drive-link-bot@PROJECT_ID.iam.gserviceaccount.com`) and grant Viewer (or Editor if uploads are needed).  
   - If the folder is not shared, the script will see zero files.

6. Configure Drive settings in `config_drive.py`  
   - Example:
     ```py
     SERVICE_ACCOUNT_JSON = "service_account.json"
     DRIVE_ROOT = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
     ```
   - You may use the raw folder ID instead of the full URL.

Notes:
- If Drive API calls return 403, confirm the Drive API is enabled and the folder is shared with the service account.
- Keep `service_account.json` private and out of version control.

## Configure the project

There are two config files to edit before running: `config.py` and `config_drive.py`.

- config.py (general downloader settings)
  - File: `config.py` (project root)
  - Edit values such as:
    - path to input CSV (e.g. INPUT_CSV or INPUT_FILE)
    - output folders for downloaded videos (e.g. VIDEOS_DIR or OUTPUT_DIR)
    - logging file (e.g. LOG_CSV or DOWNLOAD_LOG)
    - pacing and retries (e.g. SLEEP_SECONDS)
    - start index or resume position (e.g. START_INDEX)
  - Example (adjust names/values to match your `config.py` keys):
    ```
    INPUT_CSV_PATH = "creator-video-20251221_01_07_22.csv" 
    CSV_PATH = "download_log.csv"
    WL_LIST_CSV = "Mellow_WL_Live_List.csv"
    ```

- config_drive.py (Google Drive settings)
  - File: `config_drive.py` (project root)
  - Required keys:
    - `SERVICE_ACCOUNT_JSON` — filename of the service account JSON (e.g. `"service_account.json"`)
    - `DRIVE_ROOT` — Drive folder URL or folder ID
  - Example:
    ```py
    SERVICE_ACCOUNT_JSON = "service_account.json"
    DRIVE_ROOT = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"
    ```

If your `config.py` uses different variable names, edit the corresponding keys used by the code. Open the two files and update their values before running any scripts.

## Setup Environment

1. Create and activate virtualenv:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Download videos:
```bash
python3 main.py
```

2. Populate Drive links (after Drive config and sharing):
```bash
python3 drive_fill_links.py
```

3. Export/organize CSV for Notion:
```bash
python3 make_notion_csv.py
```

## What the code does (summary)

- Reads an input CSV with TikTok repost URLs.  
- Scrapes ssstik.io to obtain no‑watermark download links (fragile to site changes).  
- Downloads videos, logs results to `download_log.csv`, and places files under `videos/` (and `videos/wl/<creator>/` when configured).  
- Uses the configured Google Drive service account to link or manage Drive files per `config_drive.py`.

## Troubleshooting

- Ensure Drive API is enabled and the folder is shared with the service account.
- Do not commit `service_account.json`. Ensure it's present in the project root before running.
- If downloads fail, confirm ssstik.io scraping still works or consider using a more robust downloader method.