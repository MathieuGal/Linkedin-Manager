import time
import logging

import feedparser
import requests
from bs4 import BeautifulSoup
from convex import ConvexClient

from config import CONVEX_URL

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    "https://www.journalduhacker.net/rss",
    "https://dev.to/feed",
]


def _scrape_article_content(url: str, max_chars: int = 3000) -> str:
    """Récupère le texte principal d'un article via son URL."""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Supprimer les balises inutiles
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()

        # Chercher le contenu principal
        for selector in ["article", "main", ".post-content", ".entry-content", ".content"]:
            block = soup.select_one(selector)
            if block:
                text = block.get_text(separator=" ", strip=True)
                if len(text) > 200:
                    return text[:max_chars]

        # Fallback : tout le body
        text = soup.get_text(separator=" ", strip=True)
        return text[:max_chars]

    except Exception as exc:
        logger.warning("Impossible de scraper %s : %s", url, exc)
        return ""


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

                summary = entry.get("summary", "")
                # Si le résumé RSS est vide ou trop court, scraper l'article
                if len(summary) < 200:
                    logger.info("Résumé RSS insuffisant (%d chars), scraping de l'article...", len(summary))
                    summary = _scrape_article_content(url)
                    logger.info("Contenu scrapé (%d chars) : %.500s", len(summary), summary)

                article = {
                    "title": entry.get("title", "Sans titre"),
                    "url": url,
                    "summary": summary,
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
