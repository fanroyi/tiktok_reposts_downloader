#setup_googledrive.md

1. Create a Google Cloud Project

Go to: https://console.cloud.google.com/

Log in with your Google account

Create a new project (or select an existing one)

Example project name:

drive-video-linker

2. Enable Google Drive API

In Google Cloud Console, go to:

APIs & Services → Library


Search for Google Drive API

Click Enable

⚠️ If this step is skipped, all Drive API calls will fail (403).

3. Create a Service Account

Go to:

IAM & Admin → Service Accounts


Click Create Service Account

Fill in:

Name: drive-link-bot

Click Create and Continue

Skip role assignment (no IAM role required)

Finish creation

4. Generate service_account.json

Open the newly created Service Account

Go to the Keys tab

Click:

Add Key → Create new key → JSON


A JSON file will be downloaded automatically

✅ This file is your service_account.json

Important:

Rename it to service_account.json

Place it in the project root directory

DO NOT commit this file to Git

Add it to .gitignore

Example .gitignore:

service_account.json

5. Share Google Drive Folder with Service Account (Critical Step)

Service Accounts are not your Google user account.
They must be explicitly granted access to Drive folders.

Open Google Drive: https://drive.google.com/

Right-click the folder that contains your videos

Click Share

Copy the Service Account email (looks like this):

drive-link-bot@your-project-id.iam.gserviceaccount.com


Paste it into the Share dialog

Set permission to:

Viewer


Click Send

⚠️ If the folder is not shared, the script will see zero files.

6. Configure Drive Settings in config_drive.py

Edit config_drive.py:

SERVICE_ACCOUNT_JSON = "service_account.json"

DRIVE_ROOT = "https://drive.google.com/drive/folders/YOUR_FOLDER_ID"


You may also use the raw folder ID instead of the full URL.

