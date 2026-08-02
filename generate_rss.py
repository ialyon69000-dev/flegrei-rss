import json
import os
from datetime import datetime, timezone
from email.utils import format_datetime

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

JSON_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/events.json"
BASE_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/"

STATE_FILE = "state.json"
RSS_FILE = "feed.xml"

MAX_ITEMS = 100
TIMEOUT = 30


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"seen": []}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_events():

    r = requests.get(JSON_URL, timeout=TIMEOUT)
    r.raise_for_status()

    events = r.json()

    events.sort(
        key=lambda e: e["date"],
        reverse=True
    )

    return events


def parse_date(value):

    formats = (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    )

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            pass

    raise RuntimeError(value)


def get_magnitude(event_id):

    url = f"{BASE_URL}event_{event_id}.html"

    try:

        r = requests.get(url, timeout=TIMEOUT)

        if r.status_code != 200:
            return ""

        soup = BeautifulSoup(r.text, "lxml")

        text = soup.get_text(" ", strip=True)

        import re

        m = re.search(
            r"Magnitude[^0-9]*([0-9]+\.[0-9]+)",
            text,
            re.IGNORECASE,
        )

        if m:
            return m.group(1)

    except Exception:
        pass

    return ""


def create_feed(events):

    fg = FeedGenerator()

    fg.id(BASE_URL)

    fg.title("Campi Flegrei - GOSSIP")

    fg.link(
        href=BASE_URL,
        rel="alternate"
    )

    fg.language("fr")

    fg.description(
        "Flux RSS automatique des séismes des Campi Flegrei"
    )

    return fg
    def build_entries(fg, events, state):

    seen = set(state.get("seen", []))

    count = 0
    new_seen = []

    for ev in events:

        event_id = str(ev["id"])

        new_seen.append(event_id)

        if count >= MAX_ITEMS:
            break

        loc = ev.get("location", {})

        mag = get_magnitude(event_id)

        if mag:
            title = f"M{mag} - {ev.get('printdate', ev['date'])}"
        else:
            title = f"Séisme - {ev.get('printdate', ev['date'])}"

        description = f"""
Date : {ev.get('printdate', ev['date'])}

Latitude : {loc.get('latitude')}
Longitude : {loc.get('longitude')}
Profondeur : {loc.get('depth')} km
"""

        if mag:
            description += f"\nMagnitude : {mag}\n"

        entry = fg.add_entry()

        entry.id(event_id)

        entry.guid(event_id, permalink=False)

        entry.title(title)

        entry.description(description)

        entry.link(
            href=f"{BASE_URL}event_{event_id}.html"
        )

        dt = parse_date(ev["date"])

        entry.pubDate(format_datetime(dt))

        count += 1

    state["seen"] = new_seen[:1000]

    return state


def main():

    print("Téléchargement des événements...")

    events = load_events()

    print(f"{len(events)} événements trouvés")

    state = load_state()

    fg = create_feed(events)

    state = build_entries(
        fg,
        events,
        state
    )

    fg.rss_file(RSS_FILE)

    save_state(state)

    print("feed.xml généré")

    print("state.json mis à jour")


if __name__ == "__main__":
    main()
