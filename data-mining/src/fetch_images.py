"""Fetch one representative, openly-licensed product image per keyword bucket
(pipeline step: post-export enrichment, not part of core b1-b5 mining pipeline).

Images are illustrative only (matched by product-type keyword, e.g. "BAG",
"MUG"), not the literal real product photo -- Online Retail II ships no
product imagery. Source: Openverse (api.openverse.org), which aggregates
openly-licensed (Creative Commons) images and requires no API key. Every
image used is written to outputs/image_credits.csv with title/creator/
license/source link for proper attribution in the webapp.

Run: python3 src/fetch_images.py
Reads:  outputs/products.csv
Writes: outputs/products.csv (adds image_url column, in place)
        outputs/image_credits.csv
        data/processed/image_cache.json (cache, so re-runs don't re-fetch)
"""
from __future__ import annotations

import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_CSV = ROOT / "outputs" / "products.csv"
CREDITS_CSV = ROOT / "outputs" / "image_credits.csv"
CACHE_PATH = ROOT / "data" / "processed" / "image_cache.json"
API_URL = "https://api.openverse.org/v1/images/"
REQUEST_DELAY_SEC = 0.3

STOPWORDS = {
    "SET", "OF", "AND", "WITH", "PACK", "MINI", "LARGE", "SMALL", "MEDIUM",
    "ASSORTED", "RETROSPOT", "VINTAGE", "ANTIQUE", "DESIGN", "STYLE", "PIECE",
    "PCS", "TALL", "PINK", "RED", "BLUE", "GREEN", "WHITE", "BLACK", "YELLOW",
    "IVORY", "CREAM", "SILVER", "GOLD", "HANGING", "WALL", "TABLE", "ROUND",
    "SQUARE", "HEART", "STAR", "FLOWER", "METAL", "WOOD", "WOODEN", "GLASS",
    "CERAMIC", "PAPER", "FABRIC", "FELT", "CHRISTMAS", "EASTER", "BIRTHDAY",
    "PARTY", "GIFT", "NEW", "OLD", "RETRO", "REGENCY", "SPOTTY", "POLKADOT",
    "STRIPE", "STRIPED", "CHECK", "FLORAL",
}


def extract_keyword(description: str) -> str:
    words = re.findall(r"[A-Z']+", description.upper())
    significant = [w for w in words if w not in STOPWORDS and len(w) > 2]
    if significant:
        return significant[-1]
    tail = description.split()
    return tail[-1].upper() if tail else "ITEM"


def fetch_image_for_keyword(keyword: str) -> dict | None:
    query = urllib.parse.urlencode({
        "q": keyword, "license_type": "commercial", "page_size": 1, "mature": "false",
    })
    request = urllib.request.Request(f"{API_URL}?{query}", headers={"User-Agent": "DMML-BTL-2501/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = json.loads(response.read())
    except Exception as exc:  # network hiccups must not abort the whole batch
        print(f"  [warn] fetch failed for '{keyword}': {exc}")
        return None
    results = payload.get("results") or []
    if not results:
        return None
    top = results[0]
    return {
        "image_url": top.get("thumbnail") or top.get("url", ""),
        "title": top.get("title", ""),
        "creator": top.get("creator", ""),
        "creator_url": top.get("creator_url", ""),
        "license": f"{top.get('license', '')} {top.get('license_version', '')}".strip(),
        "license_url": top.get("license_url", ""),
        "source_url": top.get("foreign_landing_url", ""),
    }


def main() -> None:
    rows = list(csv.DictReader(PRODUCTS_CSV.open(encoding="utf-8")))
    keywords = sorted({extract_keyword(row["description"]) for row in rows})
    print(f"[images] {len(rows)} products -> {len(keywords)} unique keyword buckets")

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    cache: dict[str, dict | None] = {}
    if CACHE_PATH.exists():
        cache = json.loads(CACHE_PATH.read_text())

    fetched, found = 0, 0
    for i, keyword in enumerate(keywords, start=1):
        if keyword in cache:
            continue
        result = fetch_image_for_keyword(keyword)
        cache[keyword] = result
        fetched += 1
        found += 1 if result else 0
        if fetched % 25 == 0:
            CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2))
            print(f"  [{i}/{len(keywords)}] fetched={fetched} found={found}")
        time.sleep(REQUEST_DELAY_SEC)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2))
    print(f"[images] done fetching: {fetched} new lookups this run, {found} found this run")

    hit = sum(1 for row in rows if cache.get(extract_keyword(row["description"])))
    print(f"[images] coverage: {hit}/{len(rows)} products will show a real photo "
          f"({hit / len(rows) * 100:.1f}%)")

    fieldnames = list(rows[0].keys())
    if "image_url" not in fieldnames:
        fieldnames.append("image_url")
    tmp_products = PRODUCTS_CSV.with_name(PRODUCTS_CSV.name + ".tmp")
    with tmp_products.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            entry = cache.get(extract_keyword(row["description"]))
            row["image_url"] = entry["image_url"] if entry else ""
            writer.writerow(row)
    os.replace(tmp_products, PRODUCTS_CSV)

    tmp_credits = CREDITS_CSV.with_name(CREDITS_CSV.name + ".tmp")
    seen_urls: set[str] = set()
    with tmp_credits.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["image_url", "title", "creator", "creator_url", "license", "license_url", "source_url"])
        for entry in cache.values():
            if not entry or entry["image_url"] in seen_urls:
                continue
            seen_urls.add(entry["image_url"])
            writer.writerow([entry["image_url"], entry["title"], entry["creator"], entry["creator_url"],
                              entry["license"], entry["license_url"], entry["source_url"]])
    os.replace(tmp_credits, CREDITS_CSV)
    print(f"[images] wrote {PRODUCTS_CSV} (+image_url column) and {CREDITS_CSV} ({len(seen_urls)} distinct images)")


if __name__ == "__main__":
    main()
