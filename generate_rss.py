import requests
from feedgen.feed import FeedGenerator
from datetime import datetime

JSON_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/events.json"
BASE_URL = "https://terremoti.ov.ingv.it/gossip/flegrei/2026/"


def get_events():
    r = requests.get(JSON_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def build_feed(events):
    fg = FeedGenerator()

    fg.id("https://github.com/ialyon69000-dev/flegrei-rss")
    fg.title("Campi Flegrei - Séismes")
    fg.author({"name": "INGV"})
    fg.link(href=BASE_URL)
    fg.description("Flux RSS généré depuis les données GOSSIP de l'INGV")
    fg.language("fr")

    for ev in events[:100]:
        event_id = ev["id"]

        fe = fg.add_entry()
        fe.id(str(event_id))

        title = f"M{ev.get('magnitude','N/D')} - {ev['origin_time']}"
        fe.title(title)

        description = f"""
Latitude : {ev['latitude']}
Longitude : {ev['longitude']}
Profondeur : {ev['depth']} km
Magnitude : {ev.get('magnitude','N/D')}
Qualité : {ev.get('quality','')}
"""

        fe.description(description)

        fe.link(
            href=f"{BASE_URL}event_{event_id}.html"
        )

        dt = datetime.strptime(
            ev["origin_time"],
            "%Y/%m/%d %H:%M:%S"
        )

        fe.pubDate(dt)

    fg.rss_file("feed.xml")


if __name__ == "__main__":
    build_feed(get_events())
