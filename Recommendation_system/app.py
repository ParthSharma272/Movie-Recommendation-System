import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=d3ba7241f58f1cd4917197f50cd799b0&language=en-US'.format(movie_id))
    data = response.json()
    return "http://image.tmdb.org/t/p/w500/" + data['poster_path']
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
    return recommended_movies,recommended_poster

movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl','rb'))

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
