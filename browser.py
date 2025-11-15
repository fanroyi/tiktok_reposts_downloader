# browser.py
import time
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    return webdriver.Chrome(options=options)


# get all repost video URLs from a TikTok post link by given scrolling times
def get_repost_video_urls(
    tt_link: str,
    max_scrolls: int = 2,
    scroll_pause_time: float = 2.0,
    manual_captcha_seconds: int = 8,
    headless: bool = False,
) -> List[str]:
    print("[BROWSER INFO]: Open Chrome browser")
    driver = create_driver(headless=headless)
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
        urls = driver.execute_script(script) or []
        print(f"[BROWSER INFO]: Found {len(urls)} reposted videos")
        return urls
    finally:
        driver.quit()


def get_product_info_for_video(driver, video_url: str):
    """
    进入单个视频页面，抓取小黄车商品信息（商品名 + 链接）
    返回格式：[
        {"name": "...", "url": "..."},
        ...
    ]
    """

    print(f"\n[PRODUCT INFO]: 打开视频页面: {video_url}")
    driver.get(video_url)
    time.sleep(3)  # 等 UI 渲染

    products = []

    # -----------------------------
    # 1. 小黄车商品主卡（最常见）
    # -----------------------------
    possible_selectors = [
        # 最新 TikTok PC 版本常见结构
        'div[data-e2e="product-card"] a',

        # 旧版 TikTok 商品卡
        'div[data-e2e="video-product-anchor"] a',

        # fallback：所有链接中含 “tiktok.com/t/...” 的
        'a[href*="tiktok.com"]',
    ]

    found = False

    for selector in possible_selectors:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, selector)
            if elems and len(elems) > 0:
                print(f"[PRODUCT INFO]: 使用选择器 {selector} 找到 {len(elems)} 个商品元素")
                for el in elems:
                    name = el.text.strip()
                    href = el.get_attribute("href")

                    # 避免垃圾链接
                    if not href:
                        continue

                    # TikTok 商品跳转链接一般有 track / t / product
                    if ("product" in href or "t/" in href or "shop" in href or name) and href.startswith("http"):
                        products.append({"name": name or "(商品名为空)", "url": href})

                found = True
                break

        except Exception as e:
            print(f"[PRODUCT INFO]: 选择器 {selector} 遇到错误: {e}")

    if not found:
        print("[PRODUCT INFO]: ❌ 没找到任何小黄车商品元素")
        return []

    # 去重
    unique_products = []
    seen = set()
    for p in products:
        key = p["url"]
        if key not in seen:
            seen.add(key)
            unique_products.append(p)

    print(f"[PRODUCT INFO]: 共找到 {len(unique_products)} 个小黄车商品")
    return unique_products


def get_video_product_mapping(
    tt_link: str,
    max_scrolls: int = 2,
    scroll_pause_time: float = 2.0,
    manual_captcha_seconds: int = 8,
    headless: bool = False,
) -> List[Dict[str, object]]:
    """
    总控：
    1. 先用 get_repost_video_urls 拿到所有视频链接
       （里面会自己开一个 driver 再关掉）
    2. 再单独开一个 driver，循环每个 video_url 调 get_product_info_for_video
    3. 返回结构：
       [
         {
           "video_url": "...",
           "products": [
               {"name": "...", "url": "..."},
               ...
           ]
         },
         ...
       ]
    """

    # 第一步：拿所有 repost 视频链接
    video_urls = get_repost_video_urls(
        tt_link=tt_link,
        max_scrolls=max_scrolls,
        scroll_pause_time=scroll_pause_time,
        manual_captcha_seconds=manual_captcha_seconds,
        headless=headless,
    )

    # 第二步：开一个浏览器专门用来进每个视频抓小黄车
    driver = create_driver(headless=headless)

    results = []

    try:
        for url in video_urls:
            products = get_product_info_for_video(driver, url)
            results.append({
                "video_url": url,
                "products": products,
            })
            print("products:", products, '\n')

        return results
    finally:
        driver.quit()
        print("[BROWSER INFO]: ✅ 已关闭用于抓小黄车的浏览器")

