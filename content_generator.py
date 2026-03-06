import logging

from openai import OpenAI

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Tu es un expert en communication LinkedIn spécialisé dans la tech. "
    "Rédige un post LinkedIn en français, professionnel mais engageant, "
    "qui résume l'article fourni en 3-4 lignes, ajoute 3 hashtags pertinents "
    "liés au développement, et termine par une question ouverte pour "
    "encourager l'interaction. N'ajoute aucun titre ni préfixe au post."
)


def generate_post(title: str, summary: str) -> str:
    """Génère un post LinkedIn à partir du titre et du résumé d'un article."""
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY manquant dans le fichier .env")

    client = OpenAI(api_key=OPENAI_API_KEY)

    user_prompt = f"Titre : {title}\nDescription : {summary}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as exc:
        logger.error("Erreur lors de la génération du post : %s", exc)
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    post = generate_post(
        title="Python 3.13 introduit un nouveau garbage collector",
        summary="La nouvelle version de Python améliore les performances du GC "
                "avec un algorithme incrémental qui réduit les pauses.",
    )
    print(post)
