import streamlit as st
import pickle
import pandas as pd
import requests
import io
import os
import time

FILE_DIR = os.path.dirname(os.path.abspath(__file__))

def _abs_path(name: str) -> str:
    return os.path.join(FILE_DIR, name)

def _download_with_cache(url: str, dest_path: str, *, timeout: float = 20.0, retries: int = 3, backoff: float = 2.0) -> str:
    """Download to dest_path with simple retries. Return local path. Use existing file if present."""
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return dest_path
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            r.raise_for_status()
            tmp = dest_path + ".part"
            with open(tmp, "wb") as f:
                f.write(r.content)
            os.replace(tmp, dest_path)
            return dest_path
        except Exception as e:
            last_err = e
            if attempt < retries:
                time.sleep(backoff ** attempt)
            else:
                break
    raise RuntimeError(f"Download failed: {url} -> {dest_path}: {last_err}")

def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=d3ba7241f58f1cd4917197f50cd799b0&language=en-US',
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "http://image.tmdb.org/t/p/w500/" + poster_path
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Image"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_poster = []
    for j in movies_list:
        movie_id = movies.iloc[j[0]].movie_id
        recommended_movies.append(movies.iloc[j[0]].title)
        recommended_poster.append(fetch_poster(movie_id))
    return recommended_movies, recommended_poster

# Load movies data (prefer file next to this script, fallback to CWD)
try:
    with open(_abs_path('movie_dict.pkl'), 'rb') as f:
        movies_dict = pickle.load(f)
except FileNotFoundError:
    with open('movie_dict.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
movies = pd.DataFrame(movies_dict)

# Load similarity matrix
# Prefer local files (similarity.pkl or similarity (1).pkl), else attempt download with cache
similarity_local_candidates = [
    _abs_path('similarity.pkl'),
    _abs_path('similarity (1).pkl'),
    'similarity.pkl',
    'similarity (1).pkl',
]

similarity_path = None
for cand in similarity_local_candidates:
    if os.path.exists(cand) and os.path.getsize(cand) > 0:
        similarity_path = cand
        break

if similarity_path is None:
    similarity_url = "https://github.com/ParthSharma272/Movie-Recommendation-System/releases/download/pkl/similarity.pkl"
    try:
        similarity_path = _download_with_cache(similarity_url, _abs_path('similarity.pkl'))
    except Exception as e:
        st.error(
            "Couldn't download 'similarity.pkl' from GitHub and no local copy was found.\n"
            "Please place 'similarity.pkl' next to this script or run from a network with GitHub access.\n"
            f"Details: {e}"
        )
        st.stop()

with open(similarity_path, 'rb') as f:
    similarity = pickle.load(f)

# Streamlit page config
st.set_page_config(layout="wide")
st.title('🎥 Movie Recommendation System')
st.markdown("Welcome! Select a movie, and we'll recommend others you might like.")

# Movie selection
Selected_movie_name = st.selectbox(
    "Search for a movie:",
    movies['title'].values,
)

# Recommendation display
if st.button("Recommend"):
    with st.spinner('Fetching recommendations...'):
        names, posters = recommend(Selected_movie_name)

    st.write(f"### Recommended movies for **{Selected_movie_name}**:")

    # Dynamically create columns for full-width layout
    cols = st.columns(len(names))  # Number of columns matches the number of recommendations

    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], caption=names[idx], use_container_width=True)  # Display posters with titles as captions
