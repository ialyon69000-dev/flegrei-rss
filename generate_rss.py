import requests
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
from email.utils import format_datetime

JSON_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/events.json"
BASE_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/"


def load_events():
    response = requests.get(JSON_URL, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_date(date_str):
    """Accepte les dates avec ou sans millisecondes."""
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    raise ValueError(f"Format de date inconnu : {date_str}")


def main():
    events = load_events()

    fg = FeedGenerator()
    fg.id(BASE_URL)
    fg.title("Campi Flegrei - GOSSIP")
    fg.link(href=BASE_URL, rel="alternate")
    fg.description("Flux RSS généré automatiquement")
    fg.language("fr")

    for ev in events:

        loc = ev.get("location", {})

        entry = fg.add_entry()

        entry.id(str(ev["id"]))
        entry.title(f"Séisme {ev['id']}")

        entry.link(
            href=f"{BASE_URL}event_{ev['id']}.html",
            rel="alternate"
        )

        entry.description(
            f"""Date : {ev.get('printdate', ev.get('date'))}

Latitude : {loc.get('latitude')}
Longitude : {loc.get('longitude')}
Profondeur : {loc.get('depth')} km
"""
        )

        dt = parse_date(ev["date"])
        entry.pubDate(format_datetime(dt))

    fg.rss_file("feed.xml")

    print(f"RSS généré ({len(events)} événements)")


if __name__ == "__main__":
    main()
