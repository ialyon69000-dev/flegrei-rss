import requests
from feedgen.feed import FeedGenerator
from email.utils import format_datetime
from datetime import datetime, timezone

JSON_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/events.json"
BASE_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/"


def load_events():
    r = requests.get(JSON_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def build_feed(events):
    fg = FeedGenerator()

    fg.id(BASE_URL)
    fg.title("Campi Flegrei - GOSSIP (INGV)")
    fg.link(href=BASE_URL, rel="alternate")
    fg.description("Flux RSS généré automatiquement depuis les données GOSSIP de l'INGV")
    fg.language("fr")

    for ev in events:

        loc = ev.get("location", {})

        event_id = ev["id"]

        title = (
            f"Séisme #{event_id} - "
            f"{loc.get('depth','?')} km"
        )

        description = f"""
Date : {ev.get('printdate', ev.get('date'))}

Latitude : {loc.get('latitude')}
Longitude : {loc.get('longitude')}
Profondeur : {loc.get('depth')} km

Niveau : {ev.get('level')}
Type : {ev.get('type')}
"""

        entry = fg.add_entry()

        entry.id(str(event_id))
        entry.title(title)
        entry.description(description)

        entry.link(
            href=f"{BASE_URL}event_{event_id}.html"
        )

try:
    dt = datetime.strptime(
        ev["date"],
        "%Y-%m-%d %H:%M:%S.%f"
    )
except ValueError:
    dt = datetime.strptime(
        ev["date"],
        "%Y-%m-%d %H:%M:%S"
    )

dt = dt.replace(tzinfo=timezone.utc)

        entry.pubDate(format_datetime(dt))

    fg.rss_file("feed.xml")


if __name__ == "__main__":
    events = load_events()
    build_feed(events)
    print(f"{len(events)} événements exportés")
