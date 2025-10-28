from flask import Flask, render_template, request
import os
import pickle
import tempfile
import time

import pandas as pd
import requests

app = Flask(__name__)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(FILE_DIR, os.pardir))
CACHE_DIR = os.path.join(tempfile.gettempdir(), "movie_reco_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

RELEASE_BASE = os.environ.get(
    "MOVIE_RECO_RELEASE_BASE",
    "https://github.com/ParthSharma272/Movie-Recommendation-System/releases/download/pkl",
)
MOVIE_DICT_URL = os.environ.get("MOVIE_RECO_MOVIE_DICT_URL", f"{RELEASE_BASE}/movie_dict.pkl")
SIMILARITY_URL = os.environ.get("MOVIE_RECO_SIMILARITY_URL", f"{RELEASE_BASE}/similarity.pkl")

def _first_existing(paths):
    for p in paths:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None


def _download_with_cache(url: str, filename: str, *, retries: int = 3, timeout: float = 20.0) -> str:
    """Download url into CACHE_DIR/filename with simple retries and return the path."""
    dest_path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return dest_path

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            tmp_path = dest_path + ".part"
            with open(tmp_path, "wb") as fh:
                fh.write(resp.content)
            os.replace(tmp_path, dest_path)
            return dest_path
        except Exception as exc:  # noqa: BLE001 - surface original error message later
            last_err = exc
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                break

    raise RuntimeError(f"Failed to download {filename} from {url}: {last_err}")

# Load movie data (try local common locations)
movies_path = _first_existing([
    os.path.join(FILE_DIR, 'movie_dict.pkl'),
    os.path.join(ROOT_DIR, 'movie_dict.pkl'),
    'movie_dict.pkl',
])
if not movies_path:
    movies_path = _download_with_cache(MOVIE_DICT_URL, 'movie_dict.pkl')
with open(movies_path, 'rb') as f:
    movies_dict = pickle.load(f)
movies = pd.DataFrame(movies_dict)

# Load similarity matrix (support common '(1)' filename variant)
similarity_path = _first_existing([
    os.path.join(FILE_DIR, 'similarity.pkl'),
    os.path.join(FILE_DIR, 'similarity (1).pkl'),
    os.path.join(ROOT_DIR, 'similarity.pkl'),
    os.path.join(ROOT_DIR, 'similarity (1).pkl'),
    'similarity.pkl',
    'similarity (1).pkl',
])
if not similarity_path:
    similarity_path = _download_with_cache(SIMILARITY_URL, 'similarity.pkl')
with open(similarity_path, 'rb') as f:
    similarity = pickle.load(f)


def fetch_details(movie_id):
    """Return dict with poster, overview, rating, year, genres, runtime for a TMDB movie id."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=d3ba7241f58f1cd4917197f50cd799b0&language=en-US"
    poster = "https://via.placeholder.com/500x750?text=No+Poster"
    overview = "Description unavailable."
    rating = None
    year = None
    genres = []
    runtime = None
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            poster = f"http://image.tmdb.org/t/p/w500/{poster_path}"
        ov = data.get('overview')
        if isinstance(ov, str) and ov.strip():
            overview = ov.strip()
        try:
            vote = data.get('vote_average')
            if isinstance(vote, (int, float)):
                rating = round(float(vote), 1)
        except Exception:
            pass
        rd = data.get('release_date')
        if isinstance(rd, str) and len(rd) >= 4:
            year = rd[:4]
        gs = data.get('genres')
        if isinstance(gs, list):
            genres = [g.get('name') for g in gs if isinstance(g, dict) and g.get('name')]
        rt = data.get('runtime')
        if isinstance(rt, int) and rt > 0:
            runtime = rt
    except Exception:
        pass
    return {"poster": poster, "overview": overview, "rating": rating, "year": year, "genres": genres, "runtime": runtime}

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    items = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        details = fetch_details(movie_id)
        items.append({
            "title": title,
            "poster": details.get("poster"),
            "desc": details.get("overview"),
            "rating": details.get("rating"),
            "year": details.get("year"),
            "genres": details.get("genres", []),
            "runtime": details.get("runtime"),
        })
    return items

@app.route('/', methods=['GET', 'POST'])
def home():
    movie_titles = movies['title'].values
    if request.method == 'POST':
        selected_movie = request.form['movie_name']
        items = recommend(selected_movie)
        return render_template('index.html',
                               movie_titles=movie_titles,
                               selected_movie=selected_movie,
                               items=items)
    return render_template('index.html', movie_titles=movie_titles)

if __name__ == '__main__':
    app.run(debug=True)
