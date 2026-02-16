# config.py

# ========= Input / Output =========
INPUT_CSV_PATH = "Feb3-6_part2.csv"   # or input.csv
CSV_PATH = "download_log.csv"
WL_LIST_CSV = "Mellow_WL_Live_List.csv"
AI_LIST_CSV = "AI_Block_List.csv"

# ========= Download pacing =========
SLEEP_SECONDS = 10

# ========= Product → Subfolder override =========
# Used to map long product names to shorter subfolder names.
# Rule: if the product_value contains the key string,
#       use the corresponding value as the subfolder name.
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
}

# ========= Start number config (StdAds only) =========
# The key must exactly match product_folder
# (i.e., the output of product_to_folder()).
START_NUM_BY_FOLDER = {
    # Example: if you want CloudAlign Pillow videos
    # to start numbering from 2647
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

# StdAds: if a product folder is not configured above,
#         numbering will start from 1 by default
UNKNOWN_START_NUM = 1
