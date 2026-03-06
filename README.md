# LinkedIn Bot

Bot qui publie automatiquement sur LinkedIn un résumé d'article tech généré par IA, du lundi au vendredi à 11h00.

## Architecture

```
main.py               → orchestrateur + scheduler
news_fetcher.py        → récupère des articles via RSS, déduplique via Convex
content_generator.py   → génère le post LinkedIn via Gemini
linkedin_api.py        → publie sur LinkedIn via l'API REST v2
config.py              → charge les variables d'environnement
convex/schema.ts       → schéma de la table articles
convex/articles.ts     → fonctions query/mutation Convex
```

## Prérequis

- Docker
- Node.js 18+ (pour Convex CLI, setup uniquement)
- Un compte [Google AI Studio](https://aistudio.google.com/) avec une clé API Gemini
- Un compte [LinkedIn Developer](https://developer.linkedin.com/) avec une app configurée
- Un compte [Convex](https://www.convex.dev/) (gratuit)

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/MathieuGal/Linkedin-Manager.git
cd "Linkedin Manager"
```

### 2. Configurer Convex

```bash
npm install convex
npx convex dev
```

Au premier lancement, Convex te demandera de te connecter et de créer un projet. Note l'URL affichée dans le terminal.

### 3. Obtenir les clés API

#### Gemini

1. Aller sur https://aistudio.google.com/apikeys
2. Créer une nouvelle clé API

#### LinkedIn

1. Aller sur https://developer.linkedin.com/ et créer une app
2. Dans l'onglet **Auth**, noter le `Client ID` et `Client Secret`
3. Ajouter les produits **Share on LinkedIn** et **Sign In with LinkedIn using OpenID Connect**
4. Les scopes requis sont : `openid`, `profile`, `w_member_social`
5. Générer un Access Token via l'OAuth 2.0 flow

### 4. Remplir le fichier .env

Copier `.env` et remplacer les valeurs placeholder :

```env
# LinkedIn API
LINKEDIN_CLIENT_ID=ton_client_id
LINKEDIN_CLIENT_SECRET=ton_client_secret
LINKEDIN_ACCESS_TOKEN=ton_access_token

# Gemini API
GEMINI_API_KEY=AIza...

# Convex
CONVEX_URL=https://ton-deployment.convex.cloud
```

### 5. Lancer avec Docker

```bash
docker compose up -d --build
```

Le bot tourne en arrière-plan et redémarre automatiquement en cas de crash ou de reboot.

#### Commandes utiles

```bash
# Voir les logs en temps réel
docker compose logs -f

# Arrêter le bot
docker compose down

# Reconstruire après modification du code
docker compose up -d --build
```

## Dev local (sans Docker)

```bash
pip install -r requirements.txt
python main.py
```

## Notes

- Le token LinkedIn expire au bout de 60 jours. Il faudra le renouveler manuellement ou implémenter le refresh token flow.
- Le fuseau horaire du container est configuré sur `Europe/Paris` dans `docker-compose.yml`.
- Le fichier `.env` contient des secrets : ne jamais le commiter.
