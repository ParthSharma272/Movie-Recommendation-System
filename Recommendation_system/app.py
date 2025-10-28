from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests
import io
import os

app = Flask(__name__)

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(FILE_DIR, os.pardir))

def _first_existing(paths):
    for p in paths:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None

# Load movie data (try local common locations)
movies_path = _first_existing([
    os.path.join(FILE_DIR, 'movie_dict.pkl'),
    os.path.join(ROOT_DIR, 'movie_dict.pkl'),
    'movie_dict.pkl',
])
if not movies_path:
    raise FileNotFoundError("movie_dict.pkl not found. Place it in the project root or next to app.py")
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
    raise FileNotFoundError("similarity.pkl not found. Place it in the project root or next to app.py")
with open(similarity_path, 'rb') as f:
    similarity = pickle.load(f)


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=d3ba7241f58f1cd4917197f50cd799b0&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"http://image.tmdb.org/t/p/w500/{poster_path}"
    except Exception:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters

@app.route('/', methods=['GET', 'POST'])
def home():
    movie_titles = movies['title'].values
    if request.method == 'POST':
        selected_movie = request.form['movie_name']
        recommended_movies, recommended_posters = recommend(selected_movie)
        return render_template('index.html',
                               movie_titles=movie_titles,
                               selected_movie=selected_movie,
                               recommended_movies=recommended_movies,
                               posters=recommended_posters,
                               zip=zip)
    return render_template('index.html', movie_titles=movie_titles)

if __name__ == '__main__':
    app.run(debug=True)
