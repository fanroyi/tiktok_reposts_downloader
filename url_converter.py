import csv
import requests

input_csv = "TikTok Creator Link - Standard.csv"
output_csv = "TikTok Creator Link - Standard_full_urls.csv"

def get_full_url(short_url: str) -> str:
    """follow TikTok redirect and return final full url"""
    try:
        resp = requests.get(short_url, allow_redirects=True, timeout=10)
        return resp.url
    except Exception as e:
        print(f"Failed to convert {short_url}: {e}")
        return ""

with open(input_csv, "r", encoding="utf-8") as infile, \
     open(output_csv, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.reader(infile)
    writer = csv.writer(outfile)

    for row in reader:
        if not row:
            continue
        short = row[0].strip()
        if not short:
            continue

        full = get_full_url(short)
        print(f"{short} → {full}")

        writer.writerow([full])   # only write full URL, no header, no short URL

print("Done! Saved to:", output_csv)
