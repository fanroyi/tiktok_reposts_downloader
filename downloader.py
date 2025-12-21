# downloader.py
import os
import requests
from bs4 import BeautifulSoup


def downloadVideo(link: str, id: int, save_dir: str = "videos", filename_base: str = "unknown"):
    """
    Download TikTok video via ssstik.io
    Save to: save_dir/<filename_base>.mp4 or <filename_base>-1.mp4 ...
    Return the final file path if success, otherwise None.
    """

    cookies = {}  

    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://ssstik.io",
        "referer": "https://ssstik.io/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    params = {"url": "dl"}
    data = {
        "id": link,
        "locale": "en",
        "tt": "cG9KV3Iz",
    }

    print("[DOWNLOADING INFO]: Getting the download link")
    resp = requests.post(
        "https://ssstik.io/abc",
        params=params,
        cookies=cookies,
        headers=headers,
        data=data,
        timeout=30,
    )

    soup = BeautifulSoup(resp.text, "html.parser")

    # Find "Without watermark" download link
    try:
        result_block = soup.find("div", class_="result u-shadow--black")
        if not result_block:
            raise Exception("Missing result block (possible anti-bot / html changed).")

        overlay = result_block.find("div", class_="result_overlay pure-g")
        if not overlay:
            raise Exception("Missing overlay block.")

        btn_section = overlay.find("div", id="dl_btns")
        if not btn_section:
            raise Exception("Missing dl_btns section.")

        download_tag = btn_section.find("a", href=True, string=lambda s: s and "Without watermark" in s)
        if not download_tag:
            raise Exception("Couldn't find 'Without watermark' <a> tag.")

        download_link = download_tag["href"]
        print(f"[DOWNLOADING INFO]: ✅ Found download link {download_link}")

    except Exception as e:
        print(f"[DOWNLOADING ERROR]: ❌ Extract download link failed: {e}")
        return None

    print("[DOWNLOADING INFO]: Saving the video")
    os.makedirs(save_dir, exist_ok=True)

    file_resp = requests.get(download_link, headers=headers, stream=True, timeout=60)
    if file_resp.status_code != 200:
        print(f"[DOWNLOADING ERROR]: ❌ Failed to download video, status code: {file_resp.status_code}")
        return None

    base = filename_base or "unknown"
    filename = f"{base}.mp4"
    filepath = os.path.join(save_dir, filename)

    counter = 1
    while os.path.exists(filepath):
        filename = f"{base}-{counter}.mp4"
        filepath = os.path.join(save_dir, filename)
        counter += 1

    with open(filepath, "wb") as out:
        for chunk in file_resp.iter_content(chunk_size=8192):
            if chunk:
                out.write(chunk)

    print(f"[DOWNLOADING INFO]: ✅ Video saved: {filepath}")
    return filepath
