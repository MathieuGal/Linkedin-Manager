"""
Module de publication sur LinkedIn via l'API REST v2.

Flux utilisé :
1. GET /v2/userinfo          → récupérer le "sub" (identifiant utilisateur)
2. POST /v2/ugcPosts         → publier un post au format UGC (User Generated Content)

Docs de référence :
- https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin
- Le token doit avoir les scopes : openid, profile, w_member_social
"""

import logging

import requests

from config import LINKEDIN_ACCESS_TOKEN

logger = logging.getLogger(__name__)

BASE_URL = "https://api.linkedin.com"


def _headers() -> dict:
    """En-têtes communs à tous les appels LinkedIn."""
    if not LINKEDIN_ACCESS_TOKEN:
        raise RuntimeError("LINKEDIN_ACCESS_TOKEN manquant dans le fichier .env")
    return {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }


def _get_user_id() -> str:
    """
    Récupère l'identifiant LinkedIn de l'utilisateur authentifié.

    Endpoint : GET /v2/userinfo
    Retourne le champ "sub" qui sert d'author dans le post UGC.
    """
    resp = requests.get(f"{BASE_URL}/v2/userinfo", headers=_headers(), timeout=10)
    resp.raise_for_status()
    user_id = resp.json().get("sub")
    if not user_id:
        raise RuntimeError("Impossible de récupérer l'identifiant utilisateur LinkedIn")
    return user_id


def publish_post(text: str, article_url: str) -> dict:
    """
    Publie un post sur LinkedIn avec un lien vers l'article.

    Endpoint : POST /v2/ugcPosts
    Le body suit le format UGC Post :
    - author        → "urn:li:person:<user_id>"
    - lifecycleState → "PUBLISHED"
    - visibility     → PUBLIC (visible par tout le monde)
    - specificContent → ShareContent avec :
        - shareCommentary (le texte du post)
        - shareMediaCategory "ARTICLE"
        - media[] contenant l'URL de l'article

    Retourne le JSON de réponse LinkedIn (contient l'id du post créé).
    """
    user_id = _get_user_id()

    # --- Structure du payload UGC Post ---
    payload = {
        "author": f"urn:li:person:{user_id}",
        "lifecycleState": "PUBLISHED",
        # Visibilité : PUBLIC = visible par tous, pas seulement les connexions
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                # Le texte principal du post
                "shareCommentary": {
                    "text": text
                },
                # ARTICLE = post avec un lien cliquable en preview
                "shareMediaCategory": "ARTICLE",
                "media": [
                    {
                        "status": "READY",
                        "originalUrl": article_url,
                    }
                ],
            }
        },
    }

    resp = requests.post(
        # Endpoint de création d'un UGC Post
        f"{BASE_URL}/v2/ugcPosts",
        headers=_headers(),
        json=payload,
        timeout=15,
    )

    # --- Gestion des erreurs HTTP ---
    if resp.status_code == 201:
        logger.info("Post publié avec succès (id: %s)", resp.json().get("id"))
        return resp.json()

    # Erreurs courantes :
    # 401 → token expiré ou invalide
    # 403 → scopes insuffisants (il faut w_member_social)
    # 422 → payload malformé
    # 429 → rate limit atteint
    error_body = resp.text
    logger.error(
        "Échec de publication LinkedIn — HTTP %s : %s",
        resp.status_code,
        error_body,
    )
    resp.raise_for_status()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = publish_post(
        text=(
            "🚀 Python 3.13 améliore son garbage collector avec un algorithme "
            "incrémental qui réduit drastiquement les pauses.\n\n"
            "#Python #Performance #Dev\n\n"
            "Quel impact cela pourrait-il avoir sur vos projets ?"
        ),
        article_url="https://docs.python.org/3.13/whatsnew/3.13.html",
    )
    print("Post publié :", result.get("id"))
