# config.py

# ========= Input / Output =========
INPUT_CSV_PATH = "creator-video-20260202_22_47_30.csv"   # 或 input.csv
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
        "CloudAlign Pillow",
    
    "CloudAlign Pillow + FREE Cooling Pillowcase - Ergonomic Cervical Pillow +Dual-Height Memory Foam with Cooling Pillowcase for Side Back & Stomach Sleepers Best P":
        "CloudAlign Pillow",
    "Mellow Sleep CloudAlign Ergonomic Cervical Pillow Dual-Height Memory Foam with Cooling Pillowcase for Side Back & Stomach Sleepers Best Pillow 2025 Awarded":
        "CloudAlign Pillow",
        
    "CloudCool Cooling Blanket - Lightweight Breathable with Dual-Sided Silk Smooth & Cloud Soft Knit for Instant Cool Relief": 
        "Cooling Blanket",
        
    "Hotel Pillow Waterproof & Stain-Resistant Cloud-Soft Hypoallergenic Machine Washable Best Pillow of 2025": 
        "Hotel Pillow",
        
    "Cooling Pillowcase - Silky Smooth Wrinkle-Free Soft and Fresh All Night Sleep Enhancer": 
        "Cooling Pillowcase",

    "Cooling Pillowcase (2-Pack) - Silky Smooth Wrinkle-Free Soft and Fresh All Night Sleep Enhancer":
        "Cooling Pillowcase",
        
    "Dual-Layer Temperature Control Comforter - Super Fluffy Duvet, Lightweight & Breathable, Dual-Layer Design, OEKO-Tex Certified, Hypoallergenic, Machine Washable":
        "Temperature Control Comforter",
        
    "MarshMellow Comforter - Double-Stuffed Ultra-Soft A-Class Fabric Heat-Adaptive Vegan Fill OEKO-TEX Certified Machine Washable":
        "MarshMellow Comforter",

    "Temperature Controlling Comforter Lavender: 2 Comforter in 1, Built-In Duvet Cover, Hypoallergenic, Antibacterial Year-Round Comforter":
        "Temperature Control Comforter",

     "Temperature Controlling Comforter Navy: 2 Comforters in 1, Machine-Washable, Built-In Duvet Cover, Hypoallergenic Year-Round Comforter":
        "Temperature Control Comforter", 

    "Mellow Sleep | Dual-Layer Temperature Control Comforter - Super Fluffy Duvet, Lightweight & Breathable, Dual-Layer Design, OEKO-Tex Certified, Hypoallergenic, Machine Washable, Twin/Full/Queen/King Sizes":
        "Temperature Control Comforter", 

    "Temperature Control Comforter - 2 Comforters in 1 - Super Fluffy Duvet, Lightweight & Breathable, Dual-Layer Design, OEKO-Tex Certified, Hypoallergenic, Machine":
         "Temperature Control Comforter", 

    "Mellow Sleep | Cloud Cooling Pillowcase - Silky Smooth Wrinkle Free - Stays Cool All Night - Skin Friendly - Machine Washable - Trusted by Luxury Hotels & Spas":
        "Cloud Cooling Pillowcase",

    "Mellow Sleep |  EasyFit Sheet - Silky Soft Breathable Fitted Sheet Stays Wrinkle-Free Trusted By Top Hotels":
        "EasyFit Sheet",

    "Mellow Sleep | EasyFit Sheet - Silky Soft Breathable Fitted Sheet Stays Wrinkle-Free Trusted By Top Hotels":
         "EasyFit Sheet",

    "Adapt Pillow with 5 Sleep Zones Hotel Soft Feel Supports All Sleep Positions for Comfortable Sleep":
        "Adapt Pillow",

    "Adapt Pillow with 5 Sleep Zones Ergonomic Hotel Soft Feel Supports All Sleep Positions for Comfortable Sleep":
        "Adapt Pillow",

    "Naughty Cats: Cattitude Coloring Book for Adults and Teens": "unknown",

    "INIA GLOW Wireless LED Face Mask-with Red Light Therapy, 2-Year Warranty, Portable and Rechargeable for LED Facial Mask Skincare at Home and Travel, The Ultimate Gift Choice for this Season":"unknown",

    "Lyrically Correct Music Trivia Game - '90s & 00s Hip-Hop & R&B Edition with 140 Playing Cards & 10 Challenge Cards for Game Night Fun": "unknown",

}

# ========= Start number config (StdAds only) =========
# key 必须和 product_folder 完全一致（即 product_to_folder() 的输出）
START_NUM_BY_FOLDER = {
    # 示例：如果你想让 Cloudalign Pillow Videos 从 47 开始编号
    "CloudAlign Pillow": 2647,
    "Cooling Blanket": 3880,
    "Hotel Pillow": 4317,
    "Cooling Pillowcase": 320,
    "Temperature Control Comforter": 1960,
    "MarshMellow Comforter": 2724,
    "EasyFit Sheet": 524,
    "Adapt Pillow": 165,
    "Cloud Cooling Pillowcase": 15,
}

# StdAds: 没配置的产品 folder 默认从 1 开始
UNKNOWN_START_NUM = 1
