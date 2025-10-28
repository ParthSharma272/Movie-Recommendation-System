# 🎥 Movie Recommendation System

<img width="1680" alt="App screenshot" src="https://github.com/user-attachments/assets/ef4c300a-ce81-4f9a-a6bc-0be55b1e5a27">

A modern Flask-based web app that recommends movies you’ll love. It pairs a content-based recommendation model with TMDB metadata for posters, ratings, overviews, and more—wrapped in a sleek matte‑black + neon‑green UI.

## 🚀 Live Demo
- Vercel: https://movie-recommendation-system-lime.vercel.app/

## ✨ Features
- Smart recommendations: find similar films to any selected title
- Rich cards: poster, rating, year, genres, and runtime
- Clickable previews: modal with overview and metadata
- Favorites: heart any movie (stored locally in your browser)
- “More like this”: jump from a card into fresh related picks
- Resilient data loading: model files auto‑download from GitHub Releases in serverless environments
- Fast, responsive UI with an accessible neon dark theme

## 🧱 Tech Stack
- Backend: Flask (Python)
- Frontend: HTML/CSS/JS (Jinja templates)
- Data: pandas + pickle (`movie_dict.pkl`, `similarity.pkl`)
- Hosting: Vercel (Python Serverless Functions)
- External API: The Movie Database (TMDB)

## �️ Architecture at a Glance
- `Recommendation_system/app.py`: Flask app, recommendation logic, TMDB integration
- `Recommendation_system/templates/index.html`: neon UI, responsive grid, modal, favorites
- `api/index.py`: WSGI entrypoint for Vercel (imports the Flask `app`)
- `vercel.json`: routes all requests to the Python function

Model/data files are not stored in Git. On startup, the app looks for local pickles; if missing (e.g., on Vercel), it downloads them from GitHub Releases and caches them in `/tmp`.

Environment overrides (optional):
- `MOVIE_RECO_RELEASE_BASE` – Base URL for release assets
- `MOVIE_RECO_MOVIE_DICT_URL` – Full URL to `movie_dict.pkl`
- `MOVIE_RECO_SIMILARITY_URL` – Full URL to `similarity.pkl`

## 🧪 Running Locally
Prerequisites: Python 3.10+ on macOS/Linux/Windows

1) Create a virtual environment and install deps

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) Start the Flask app

```bash
python Recommendation_system/app.py
```

3) Open http://127.0.0.1:5000 in your browser

Notes:
- The app will try local pickle files first; if absent, it will download them.
- TMDB requests use a built-in API key in this version. For production, consider moving it to an environment variable.

## ☁️ Deploying on Vercel
This repo already includes the required wiring.

- Import the repo in Vercel (or run `vercel` from the project root)
- No build step needed—Vercel routes all requests to `api/index.py`
- Cold starts may download model files once and cache them in `/tmp`
- Optionally set the environment variables listed above to point at your own release assets

## 🔐 Data & Credits
- Posters, ratings, and metadata are fetched from TMDB. This product uses the TMDB API but is not endorsed or certified by TMDB.
- Recommendation data comes from precomputed pickles (`movie_dict.pkl`, `similarity.pkl`).

## 📄 License
MIT — see `LICENSE`.

---
Questions or ideas? Open an issue or reach out via discussions. Enjoy the movies! 🍿



