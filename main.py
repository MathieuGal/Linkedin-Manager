import time
import logging

import schedule

from news_fetcher import fetch_latest_article
from content_generator import generate_post
from linkedin_api import publish_post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """Flux complet : article → post IA → publication LinkedIn."""
    logger.info("Lancement du pipeline")

    # 1. Récupérer un article inédit
    article = fetch_latest_article()
    if not article:
        logger.info("Aucun nouvel article, pipeline terminé.")
        return

    logger.info("Article trouvé : %s", article["title"])

    # 2. Générer le post avec l'IA
    post_text = generate_post(article["title"], article["summary"])
    logger.info("Post généré (%d caractères)", len(post_text))

    # 3. Publier sur LinkedIn
    result = publish_post(post_text, article["url"])
    logger.info("Publié sur LinkedIn — id: %s", result.get("id"))


# --- Planification : lundi à vendredi à 11h00 ---
schedule.every().monday.at("11:00").do(run_pipeline)
schedule.every().tuesday.at("11:00").do(run_pipeline)
schedule.every().wednesday.at("11:00").do(run_pipeline)
schedule.every().thursday.at("11:00").do(run_pipeline)
schedule.every().friday.at("11:00").do(run_pipeline)

if __name__ == "__main__":
    logger.info("Bot LinkedIn démarré — publication lun-ven à 11h00")
    logger.info("Prochaine exécution : %s", schedule.next_run())

    while True:
        schedule.run_pending()
        time.sleep(60)
