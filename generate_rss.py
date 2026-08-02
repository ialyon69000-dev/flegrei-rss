import json
from pathlib import Path
from datetime import datetime, timezone
from email.utils import format_datetime

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

JSON_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/events.json"
BASE_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/"
STATE_FILE = Path("state.json")
MAX_ITEMS = 100


def load_events():
    r = requests.get(JSON_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"seen_ids": [], "items": []}


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def parse_date(date_str):
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    raise ValueError(f"Format de date inconnu : {date_str}")


def fetch_magnitude(event_id):
    url = f"{BASE_URL}event_{event_id}.html"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    for row in soup.select(".magnitudo_row"):
        text = " ".join(row.stripped_strings)
        if text:
            return text

    return None


def build_item(ev):
    loc = ev.get("location", {})
    event_id = ev["id"]

    magnitude = fetch_magnitude(event_id) or "N/D"

    dt = parse_date(ev["date"])

    return {
        "id": event_id,
        "title": f"Séisme #{event_id} - M {magnitude}",
        "link": f"{BASE_URL}event_{event_id}.html",
        "description": (
            f"Date : {ev.get('printdate', ev.get('date'))}\n\n"
            f"Latitude : {loc.get('latitude')}\n"
            f"Longitude : {loc.get('longitude')}\n"
            f"Profondeur : {loc.get('depth')} km\n"
            f"Magnitude : {magnitude}\n"
            f"Niveau : {ev.get('level')}\n"
        ),
        "pubDate": format_datetime(dt),
        "epoch": ev.get("epoch", dt.timestamp()),
    }


def generate_feed(items):
    fg = FeedGenerator()
    fg.id(BASE_URL)
    fg.title("Campi Flegrei - GOSSIP (INGV)")
    fg.link(href=BASE_URL, rel="alternate")
    fg.description("Flux RSS généré automatiquement depuis les données GOSSIP de l'INGV")
    fg.language("fr")

    for item in items:
        fe = fg.add_entry()
        fe.id(str(item["id"]))
        fe.title(item["title"])
        fe.link(href=item["link"])
        fe.description(item["description"])
        fe.pubDate(item["pubDate"])

    fg.rss_file("feed.xml")


def main():
    events = load_events()
    state = load_state()

    seen = set(state.get("seen_ids", []))
    items = state.get("items", [])

    new_count = 0

    for ev in events:
        if ev["id"] in seen:
            continue

        item = build_item(ev)
        items.insert(0, item)
        seen.add(ev["id"])
        new_count += 1

    items.sort(key=lambda x: x["epoch"], reverse=True)
    items = items[:MAX_ITEMS]

    state = {
        "seen_ids": sorted(seen),
        "items": items,
    }

    save_state(state)
    generate_feed(items)

    print(f"Nouveaux événements : {new_count}")
    print(f"Flux RSS généré avec {len(items)} éléments")


if __name__ == "__main__":
    main()
