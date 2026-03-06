# LinkedIn Bot

Bot qui publie automatiquement sur LinkedIn un résumé d'article tech généré par IA, du lundi au vendredi à 11h00.

## Architecture

```
main.py               → orchestrateur + scheduler
news_fetcher.py        → récupère des articles via RSS, déduplique via Convex
content_generator.py   → génère le post LinkedIn via OpenAI
linkedin_api.py        → publie sur LinkedIn via l'API REST v2
config.py              → charge les variables d'environnement
convex/schema.ts       → schéma de la table articles
convex/articles.ts     → fonctions query/mutation Convex
```

## Prérequis

- Python 3.10+
- Node.js 18+ (pour Convex CLI)
- Un compte [OpenAI](https://platform.openai.com/) avec une clé API
- Un compte [LinkedIn Developer](https://developer.linkedin.com/) avec une app configurée
- Un compte [Convex](https://www.convex.dev/) (gratuit)

## Installation

### 1. Cloner le projet et installer les dépendances Python

```bash
git clone <url-du-repo>
cd "Linkedin Manager"
pip install -r requirements.txt
```

### 2. Configurer Convex

```bash
npm install convex
npx convex dev
```

Au premier lancement, Convex te demandera de te connecter et de créer un projet. Une fois déployé, note l'URL affichée dans le terminal (ex: `https://abc-123.convex.cloud`).

### 3. Obtenir les clés API

#### OpenAI

1. Aller sur https://platform.openai.com/api-keys
2. Créer une nouvelle clé API
3. Copier la clé

#### LinkedIn

1. Aller sur https://developer.linkedin.com/ et créer une app
2. Dans l'onglet **Auth**, noter le `Client ID` et `Client Secret`
3. Ajouter les produits **Share on LinkedIn** et **Sign In with LinkedIn using OpenID Connect**
4. Les scopes requis sont : `openid`, `profile`, `w_member_social`
5. Générer un Access Token via l'OAuth 2.0 flow (ou les outils de test LinkedIn)

### 4. Remplir le fichier .env

Ouvrir `.env` et remplacer les valeurs placeholder :

```env
# LinkedIn API
LINKEDIN_CLIENT_ID=ton_client_id
LINKEDIN_CLIENT_SECRET=ton_client_secret
LINKEDIN_ACCESS_TOKEN=ton_access_token

# OpenAI API
OPENAI_API_KEY=sk-...

# Convex
CONVEX_URL=https://ton-deployment.convex.cloud
```

### 5. Lancer le bot

```bash
python main.py
```

Le bot affiche la prochaine exécution planifiée et tourne en continu. Il publie automatiquement du lundi au vendredi à 11h00.

## Test rapide (publication immédiate)

Pour tester chaque module individuellement :

```bash
# Tester la récupération d'articles
python news_fetcher.py

# Tester la génération de post
python content_generator.py

# Tester la publication LinkedIn
python linkedin_api.py
```

## Notes

- Le token LinkedIn expire au bout de 60 jours. Il faudra le renouveler manuellement ou implémenter le refresh token flow.
- Le scheduler utilise l'heure locale de la machine. Vérifie que le fuseau horaire est correct.
- Le fichier `.env` contient des secrets : ne jamais le commiter. Ajouter `.env` dans `.gitignore`.
