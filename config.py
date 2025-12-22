# config.py

# ========= Input / Output =========
INPUT_CSV_PATH = "creator-video-20251221_01_07_22.csv"   # 或 input.csv
CSV_PATH = "download_log.csv"
WL_LIST_CSV = "Mellow_WL_Live_List.csv"
AI_LIST_CSV = "AI_Block_List.csv"

# ========= Download pacing =========
SLEEP_SECONDS = 10

# ========= Product → Subfolder override =========
# 用于把“超长 product 名”映射成你希望的短 subfolder 名字
# 规则：只要 product_value 里包含 key，就使用 val 作为 subfolder
PRODUCT_SUBFOLDER_MAP = {
    "Cloud Pillow + FREE Cooling Pillowcase - Ergonomic Cervical Dual-Height Slow-Rebound Memory Foam with Washable Cover for Side Back & Stomach Sleepers Best Pillo":
        "Cloudalign Pillow Videos",
        
    "CloudCool Cooling Blanket - Lightweight Breathable with Dual-Sided Silk Smooth & Cloud Soft Knit for Instant Cool Relief": 
        "CloudCool Cooling Blanket Videos",
        
    "Hotel Pillow Waterproof & Stain-Resistant Cloud-Soft Hypoallergenic Machine Washable Best Pillow of 2025": 
        "Hotel Pillow Waterproof & Stain-Resistant Cloud-Soft Hypoallergenic",
        
    "Cooling Pillowcase - Silky Smooth Wrinkle-Free Soft and Fresh All Night Sleep Enhancer": 
        "Cooling Pillowcase",
        
    "Dual-Layer Temperature Control Comforter - Super Fluffy Duvet, Lightweight & Breathable, Dual-Layer Design, OEKO-Tex Certified, Hypoallergenic, Machine Washable":
        "Dual-Layer Temperature Control Comforter",
        
    "Hotel Pillow Waterproof & Stain-Resistant Cloud-Soft Hypoallergenic Machine Washable Best Pillow of 2025":
        "Hotel Pillow Waterproof",
        
    "MarshMellow Comforter - Double-Stuffed Ultra-Soft A-Class Fabric Heat-Adaptive Vegan Fill OEKO-TEX Certified Machine Washable":
        "MarshMellow Comforter",
}

# ========= Start number config (StdAds only) =========
# key 必须和 product_folder 完全一致（即 product_to_folder() 的输出）
START_NUM_BY_FOLDER = {
    # 示例：如果你想让 Cloudalign Pillow Videos 从 47 开始编号
    "Cloudalign Pillow Videos": 47,
    "CloudCool Cooling Blanket - Lightweight Breathable with Dual-Sided Silk Smooth & Cloud Soft Knit for Instant Cool Relief": 47,
    "Hotel Pillow Waterproof & Stain-Resistant Cloud-Soft Hypoallergenic Machine Washable Best Pillow of 2025": 23,
    # product3 不写 -> 默认从 UNKNOWN_START_NUM 开始
}

# StdAds: 没配置的产品 folder 默认从 1 开始
UNKNOWN_START_NUM = 1
