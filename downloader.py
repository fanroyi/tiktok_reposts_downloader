import re
from bs4 import BeautifulSoup
import requests
import os


def downloadVideo(link, id):
    cookies = {
        # [Your cookie data if needed]
    }

    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'hx-current-url': 'https://ssstik.io/',
        'hx-request': 'true',
        'hx-target': 'target',
        'hx-trigger': '_gcaptcha_pt',
        'origin': 'https://ssstik.io',
        'referer': 'https://ssstik.io/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }

    params = {
        'url': 'dl',
    }

    data = {
        'id': link,
        'locale': 'en',
        'tt': 'cG9KV3Iz',
    }

    print("[DOWNLOADING INFO]: Getting the download link")

    response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
    downloadSoup = BeautifulSoup(response.text, "html.parser")

    # Try to extract the original username
    original_author = "unknown"
    try:
        original_author = '@'+link.split("/")[3].lstrip("@")
    except Exception as e:
        print(f"[DOWNLOADING ERROR]: ❌ Could not extract original author: {e}")

    try:
        result_block = downloadSoup.find("div", class_="result u-shadow--black")
        overlay = result_block.find("div", class_="result_overlay pure-g")
        btn_section = overlay.find("div", id="dl_btns")
        download_tag = btn_section.find("a", href=True, string=lambda s: "Without watermark" in s)

        if download_tag:
            downloadLink = download_tag["href"]
            print(f"[DOWNLOADING INFO]: ✅ Found download link from ssstik.io {downloadLink}")
        else:
            raise Exception("[DOWNLOADING ERROR]: ❌ Couldn't find the <a> tag with download link.")

    except Exception as e:
        print("[DOWNLOADING ERROR]: ❌ Error while extracting download link from html:", e)
        return None

    try:
        raw_title = downloadSoup.p.getText().strip()
    except:
        raw_title = f"video_{id}"

    safe_title = re.sub(r'[\\/*?:"<>|]', "", raw_title)[:80]  # remove illegal chars and limit length

    print("[DOWNLOADING INFO]: Saving the video")

    resp_file = requests.get(downloadLink, headers=headers, stream=True)

    if resp_file.status_code == 200:

        # ✅ 自动处理重复文件名逻辑
        base_name = original_author
        filename = f"{base_name}.mp4"
        filepath = os.path.join("videos", filename)

        counter = 1
        while os.path.exists(filepath):
            filename = f"{base_name}-{counter}.mp4"
            filepath = os.path.join("videos", filename)
            counter += 1

        # ✅ filepath 已经是 final 的文件名（author.mp4 或 author-1.mp4 或 author-2.mp4...）

        with open(filepath, "wb") as output:
            for chunk in resp_file.iter_content(chunk_size=8192):
                if chunk:
                    output.write(chunk)

        print(f"[DOWNLOADING INFO]: ✅ Video saved: {filepath}")
        return filepath  # ✅ 返回最终文件路径

    else:
        print(f"[DOWNLOADING ERROR]: ❌ Failed to download video, status code: {resp_file.status_code}")
        return None



# previous working-----
# import re
# from bs4 import BeautifulSoup
# import requests


# def downloadVideo(link, id):
#     cookies = {
#         # [Your cookie data if needed]
#     }

#     headers = {
#         'accept': '*/*',
#         'accept-language': 'en-US,en;q=0.9',
#         'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
#         'hx-current-url': 'https://ssstik.io/',
#         'hx-request': 'true',
#         'hx-target': 'target',
#         'hx-trigger': '_gcaptcha_pt',
#         'origin': 'https://ssstik.io',
#         'referer': 'https://ssstik.io/',
#         'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
#     }

#     params = {
#         'url': 'dl',
#     }

#     data = {
#         'id': link,
#         'locale': 'en',
#         'tt': 'cG9KV3Iz',
#     }

#     print("[DOWNLOADING INFO]: Getting the download link")

#     response = requests.post('https://ssstik.io/abc', params=params, cookies=cookies, headers=headers, data=data)
#     downloadSoup = BeautifulSoup(response.text, "html.parser")

#     # Try to extract the original username
#     original_author = "unknown"
#     try:
#         original_author = link.split("/")[3]
#     except Exception as e:
#         print(f"[DOWNLOADING ERROR]: ❌ Could not extract original author: {e}")

#     try:
#         result_block = downloadSoup.find("div", class_="result u-shadow--black")
#         overlay = result_block.find("div", class_="result_overlay pure-g")
#         btn_section = overlay.find("div", id="dl_btns")
#         download_tag = btn_section.find("a", href=True, string=lambda s: "Without watermark" in s)

#         if download_tag:
#             downloadLink = download_tag["href"]
#             print(f"[DOWNLOADING INFO]: ✅ Found download link from ssstik.io {downloadLink}")
#         else:
#             raise Exception("[DOWNLOADING ERROR]: ❌ Couldn't find the <a> tag with download link.")

#     except Exception as e:
#         print("[DOWNLOADING ERROR]: ❌ Error while extracting download link from html:", e)
#         return

#     try:
#         raw_title = downloadSoup.p.getText().strip()
#     except:
#         raw_title = f"video_{id}"

#     safe_title = re.sub(r'[\\/*?:"<>|]', "", raw_title)[:80]  # remove illegal chars and limit length



#     print("[DOWNLOADING INFO]: Saving the video")

#     response = requests.get(downloadLink, headers=headers, stream=True)

#     if response.status_code == 200:
#         #filepath = f"videos/{id}-{safe_title} [by {original_author}].mp4"
#         filepath = f"videos/{original_author}.mp4"
#         with open(filepath, "wb") as output:
#             for chunk in response.iter_content(chunk_size=8192):
#                 if chunk:
#                     output.write(chunk)
#         print(f"[DOWNLOADING INFO]: ✅ Video saved: {filepath}")
#         return True
#     else:
#         print(f"[DOWNLOADING ERROR]: ❌ Failed to download video, status code: {response.status_code}")
#         return

