import logging

from google import genai
from google.genai import types

from pathlib import Path

from config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).parent / "prompt.txt"


def _load_prompt() -> str:
    if not PROMPT_FILE.exists():
        raise RuntimeError(f"Fichier prompt introuvable : {PROMPT_FILE}")
    return PROMPT_FILE.read_text(encoding="utf-8").strip()


def generate_post(title: str, summary: str) -> str:
    """Génère un post LinkedIn à partir du titre et du résumé d'un article."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY manquant dans le fichier .env")

    client = genai.Client(api_key=GEMINI_API_KEY)

    user_prompt = f"Titre : {title}\nDescription : {summary}"

    logger.info("Prompt envoyé à Gemini :\n%s", user_prompt[:1000])

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=_load_prompt(),
                max_output_tokens=8192,
                temperature=0.7,
            ),
        )

        candidate = response.candidates[0]
        finish_reason = candidate.finish_reason
        logger.info("Gemini finish_reason : %s", finish_reason)
        logger.info("Gemini réponse brute :\n%s", response.text)

        return response.text.strip()

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
