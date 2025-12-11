# browser.py
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_repost_video_urls(
    tt_link: str,
    max_scrolls: int = 2,
    scroll_pause_time: float = 2.0,
    manual_captcha_seconds: int = 8,
    headless: bool = False,
):
    print("[BROWSER INFO]: Open Chrome browser")
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(tt_link)
        print("[BROWSER INFO]: ✅ 页面打开，等待加载和手动处理验证码（如果有）...")
        time.sleep(manual_captcha_seconds)

        try:
            print("[BROWSER INFO]: ⏳ 等待并点击 Reposts 标签...")
            repost_tab = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "p[data-e2e='repost-tab']"))
            )
            repost_tab.click()
            print("[BROWSER INFO]: ✅ 已点击 Reposts 标签，等待内容加载...")
        except Exception as e:
            print("[BROWSER ERROR]: ❌ 点击 Reposts 标签失败:", e)

        time.sleep(2)

        print("[BROWSER INFO]: Scrolling page until all repost videos load")
        last_height = driver.execute_script("return document.body.scrollHeight")
        for i in range(max_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print(f"[BROWSER INFO]: No more content after {i} scrolls")
                break
            last_height = new_height
        else:
            print("[BROWSER INFO]: Reached max scroll limit")
        print("[BROWSER INFO]: ✅ Finished scrolling full page")

        script = """
            return Array.from(document.querySelectorAll('a[href*="/video/"]'))
                .map(el => el.href)
                .filter((v, i, a) => a.indexOf(v) === i);
        """
        urls = driver.execute_script(script) or [] #[link1, link2 , ...]
        print(f"[BROWSER INFO]: Found {len(urls)} reposted videos")
        return urls
    finally:
        driver.quit()
