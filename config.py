# config.py

# ========= Input / Output =========
INPUT_CSV_PATH = "creator-video-20251215_08_50_49.csv"   # 或 input.csv
CSV_PATH = "download_log.csv"
WL_LIST_CSV = "Mellow_WL_Live_List.csv"

# ========= Download pacing =========
SLEEP_SECONDS = 10

# ========= Start number config (StdAds only) =========
# key 必须和 product_folder 完全一致（即 Product 列 '|' 右侧文本清理后的结果）
START_NUM_BY_FOLDER = {
    # 写你已知的产品起始编号
    "CloudCool Cooling Blanket - Lightweight Breathable with Dual-Sided Silk Smooth & Cloud Soft Knit for Instant Cool Relief": 47,
    "Hotel Pillow Waterproof & Stain-Resistant Cloud-Soft Hypoallergenic Machine Washable Best Pillow of 2025": 23,
    # product3 不写 -> 默认从 UNKNOWN_START_NUM 开始
}

# StdAds: 没配置的产品 folder 默认从 1 开始
UNKNOWN_START_NUM = 1
