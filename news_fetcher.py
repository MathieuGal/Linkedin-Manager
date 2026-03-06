import time
import logging

import feedparser
from convex import ConvexClient

from config import CONVEX_URL

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    "https://www.journalduhacker.net/rss",
    "https://dev.to/feed",
]


def _get_client() -> ConvexClient:
    if not CONVEX_URL:
        raise RuntimeError("CONVEX_URL manquant dans le fichier .env")
    return ConvexClient(CONVEX_URL)


def _is_already_saved(client: ConvexClient, url: str) -> bool:
    result = client.query("articles:getByUrl", {"url": url})
    return result is not None


def _save_article(client: ConvexClient, title: str, url: str, summary: str) -> None:
    client.mutation("articles:insert", {
        "url": url,
        "title": title,
        "summary": summary,
        "fetched_at": time.time(),
    })


def fetch_latest_article() -> dict | None:
    """Parcourt les flux RSS et retourne le premier article non encore enregistré."""
    client = _get_client()

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as exc:
            logger.error("Erreur lors du parsing de %s : %s", feed_url, exc)
            continue

        if feed.bozo and not feed.entries:
            logger.warning("Flux invalide ou vide : %s", feed_url)
            continue

        for entry in feed.entries:
            url = entry.get("link")
            if not url:
                continue

            try:
                if _is_already_saved(client, url):
                    logger.debug("Déjà en base : %s", url)
                    continue

                article = {
                    "title": entry.get("title", "Sans titre"),
                    "url": url,
                    "summary": entry.get("summary", ""),
                }

                _save_article(client, article["title"], url, article["summary"])
                logger.info("Nouvel article enregistré : %s", article["title"])
                return article

            except Exception as exc:
                logger.error("Erreur Convex pour %s : %s", url, exc)
                continue

    logger.info("Aucun nouvel article trouvé.")
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    article = fetch_latest_article()
    if article:
        print(f"\nTitre   : {article['title']}")
        print(f"Lien    : {article['url']}")
        print(f"Résumé  : {article['summary'][:200]}")
    else:
        print("Aucun nouvel article à traiter.")
