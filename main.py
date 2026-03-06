import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path

import schedule

from news_fetcher import fetch_latest_article
from content_generator import generate_post
from linkedin_api import publish_post

POSTS_DIR = Path("posts")
POSTS_DIR.mkdir(exist_ok=True)

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

    logger.info("Résumé récupéré (%d caractères) : %.300s", len(article["summary"]), article["summary"])

    # 2. Générer le post avec l'IA
    post_text = generate_post(article["title"], article["summary"])
    logger.info("Post généré (%d caractères) :\n%s", len(post_text), post_text)

    # 3. Sauvegarder le post en JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    post_file = POSTS_DIR / f"{timestamp}.json"
    post_data = {
        "generated_at": datetime.now().isoformat(),
        "article_title": article["title"],
        "article_url": article["url"],
        "post_text": post_text,
        "linkedin_post_id": None,
    }
    post_file.write_text(json.dumps(post_data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Post sauvegardé : %s", post_file)

    # 4. Publier sur LinkedIn
    result = publish_post(post_text)
    post_data["linkedin_post_id"] = result.get("id")
    post_file.write_text(json.dumps(post_data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Publié sur LinkedIn — id: %s", result.get("id"))


# --- Planification : lundi à vendredi à 11h00 ---
schedule.every().monday.at("11:00").do(run_pipeline)
schedule.every().tuesday.at("11:00").do(run_pipeline)
schedule.every().wednesday.at("11:00").do(run_pipeline)
schedule.every().thursday.at("11:00").do(run_pipeline)
schedule.every().friday.at("11:00").do(run_pipeline)

if __name__ == "__main__":
    if "--now" in sys.argv:
        logger.info("Mode test : exécution immédiate du pipeline")
        run_pipeline()
    else:
        logger.info("Bot LinkedIn démarré — publication lun-ven à 11h00")
        logger.info("Prochaine exécution : %s", schedule.next_run())

        while True:
            schedule.run_pending()
            time.sleep(60)
