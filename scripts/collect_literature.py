import csv
import json
import re
import time
from collections import OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT_CSV = DOCS / "related_work_matrix.csv"
OUT_JSON = DOCS / "related_work_matrix.json"
LOG = DOCS / "literature_collect_log.txt"

QUERIES = [
    "micro slip tactile manipulation",
    "slip state estimation robot manipulation",
    "contact state estimation dexterous manipulation",
    "tactile slip detection robotic grasp",
    "contact rich manipulation state estimation",
    "force tactile proprioceptive manipulation",
    "object pose contact state estimation manipulation",
    "latent state manipulation tactile sensing",
    "slip detection grasp control robot",
    "micro slip dexterous manipulation",
    "robotic hand slip estimation tactile",
    "manipulation contact dynamics estimation",
    "robot grasp tactile sensing",
    "robot tactile feedback manipulation",
    "force control contact estimation robot",
    "dexterous grasp pose estimation",
    "in-hand manipulation object pose estimation",
    "robot compliance estimation contact",
    "friction estimation tactile robotics",
    "haptic sensing manipulation robot",
    "proprioceptive tactile sensing robot hand",
    "contact-rich manipulation robotics",
    "robot hand object pose force sensing",
    "tactile object recognition manipulation",
    "slip prediction robotic grasping",
    "contact mechanics robotics manipulation",
    "force estimation robot hand",
    "tactile servoing grasping",
]

KEYWORDS = {
    "slip": ["slip", "micro slip", "incipient slip"],
    "tactile": ["tactile", "haptic", "touch", "skin"],
    "contact": ["contact", "force", "wrench", "pressure"],
    "state": ["state estimation", "latent state", "belief", "filter", "observer"],
    "manipulation": ["manipulation", "grasp", "dexterous", "hand", "gripper"],
    "dynamics": ["object dynamics", "friction", "compliance", "pose"],
}


def log(msg: str) -> None:
    DOCS.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")


def normalize_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title or "").strip().lower()
    return title


def score_item(item: dict) -> tuple[int, list[str]]:
    text = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("container", "")),
            " ".join(item.get("authors", [])),
        ]
    ).lower()
    score = 0
    tags = []
    for tag, words in KEYWORDS.items():
        hits = sum(1 for w in words if w in text)
        if hits:
            score += hits
            tags.append(tag)
    return score, tags


def crossref_query(q: str, rows: int = 100, cursor: str | None = None) -> dict:
    params = {
        "query.bibliographic": q,
        "rows": rows,
        "select": "DOI,title,author,container-title,issued,URL,type",
    }
    if cursor:
        params["cursor"] = cursor
        params["cursor-max"] = 1000
    url = "https://api.crossref.org/works"
    r = requests.get(url, params=params, timeout=60, headers={"User-Agent": "CodexResearchBot/1.0 (mailto:research@example.com)"})
    r.raise_for_status()
    return r.json()


def extract_year(item: dict) -> str:
    issued = item.get("issued", {}).get("date-parts", [])
    if issued and issued[0]:
        return str(issued[0][0])
    return ""


def extract_authors(item: dict) -> str:
    authors = []
    for a in item.get("author", [])[:8]:
        given = a.get("given", "").strip()
        family = a.get("family", "").strip()
        name = " ".join(x for x in [given, family] if x)
        if name:
            authors.append(name)
    return "; ".join(authors)


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    seen = OrderedDict()
    buckets = defaultdict(int)
    collected = []
    log("starting Crossref sweep")

    for query in QUERIES:
        cursor = None
        for page in range(10):
            try:
                data = crossref_query(query, rows=100, cursor=cursor)
            except Exception as e:
                log(f"query failed: {query} page={page} err={e}")
                break
            msg = data.get("message", {})
            items = msg.get("items", [])
            cursor = msg.get("next-cursor")
            if not items:
                break
            for it in items:
                title = (it.get("title") or [""])[0].strip()
                if not title:
                    continue
                year = extract_year(it)
                doi = it.get("DOI", "")
                key = normalize_title(title) + "|" + year + "|" + doi.lower()
                if key in seen:
                    continue
                authors = extract_authors(it)
                venue = (it.get("container-title") or [""])[0].strip()
                text_score, tags = score_item({
                    "title": title,
                    "container": venue,
                    "authors": authors,
                })
                seen[key] = {
                    "query": query,
                    "title": title,
                    "year": year,
                    "venue": venue,
                    "authors": authors,
                    "doi": doi,
                    "url": it.get("URL", ""),
                    "type": it.get("type", ""),
                    "source": "Crossref",
                    "score": text_score,
                    "tags": ";".join(tags),
                }
                buckets[query] += 1
                collected.append(seen[key])
            log(f"query={query} page={page} cumulative={len(seen)}")
            if len(seen) >= 2200:
                break
            time.sleep(0.15)
        if len(seen) >= 2200:
            break

    # Add a few high-confidence tactile/manipulation papers from arXiv-ish naming if available through Crossref
    rows = list(seen.values())
    rows.sort(key=lambda r: (r["score"], r["year"]), reverse=True)
    # Keep a balanced but top-biased set.
    final = rows[:2200] if len(rows) > 2200 else rows
    # Write CSV
    fieldnames = ["query", "title", "year", "venue", "authors", "doi", "url", "type", "source", "score", "tags"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(final, f, indent=2, ensure_ascii=True)
    log(f"wrote {len(final)} rows to {OUT_CSV.name}")
    print(len(final))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
