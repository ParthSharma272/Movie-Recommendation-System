from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests
import io

app = Flask(__name__)

# Load movie data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

# Load similarity matrix from GitHub
similarity = pickle.load(open('similarity.pkl', 'rb'))


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=d3ba7241f58f1cd4917197f50cd799b0&language=en-US"
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"http://image.tmdb.org/t/p/w500/{poster_path}"
    else:
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
