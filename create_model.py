import pickle
import streamlit as st
import requests
import pandas as pd

# -----------------------------
# TMDB API Key
# -----------------------------
API_KEY = "53665942eec85abad6abcb0407f79c90"

def fetch_poster(movie_id):
    """Fetches the movie poster URL from TMDB API."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500" + poster_path
            return full_path
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
    
    # Return a placeholder if the poster is not found or an error occurs
    return "https://placehold.co/500x750/333/FFFFFF?text=No+Poster"

def recommend(movie):
    """Recommends 5 similar movies based on the selected movie."""
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error("Movie not found in the dataset. Please select another one.")
        return [], [], [], []
        
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_years = []
    recommended_movie_ratings = []

    for i in distances[1:6]:
        # fetch the movie details
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]]['title'])
        recommended_movie_years.append(movies.iloc[i[0]]['year'])
        recommended_movie_ratings.append(movies.iloc[i[0]]['vote_average'])

    return recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(layout="wide")
st.header('🎬 Movie Recommender System Using Machine Learning')

# Load the data files
try:
    movies_dict = pickle.load(open('model/movie_list.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error("Model files not found. Please make sure movie_list.pkl and similarity.pkl exist in the 'model' folder.")
    st.stop()

# Movie selection
movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

# Show recommendations
if st.button('Show Recommendation'):
    with st.spinner('Finding recommendations...'):
        recommended_movie_names, recommended_movie_posters, recommended_movie_years, recommended_movie_ratings = recommend(selected_movie)
    
    if recommended_movie_names:
        cols = st.columns(5)
        for i, col in enumerate(cols):
            with col:
                st.text(recommended_movie_names[i])
                st.image(recommended_movie_posters[i])
                
                year = recommended_movie_years[i]
                if pd.notna(year):
                    st.caption(f"Year: {int(year)}")
                else:
                    st.caption("Year: N/A")
                
                rating = recommended_movie_ratings[i]
                st.caption(f"Rating: {rating:.1f} ⭐")


