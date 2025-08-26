import pickle
import streamlit as st
import requests
import pandas as pd
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Perfect Pitch - Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data globally
try:
    movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading movie data: {str(e)}")
    movies = None
    similarity = None

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    
    .movie-title {
        font-weight: bold;
        font-size: 1.1rem;
        margin: 0.5rem 0;
        color: #333;
        text-align: center;
        line-height: 1.3;
    }
    
    .movie-poster {
        border-radius: 10px;
        width: 100%;
        height: auto;
    }
    
    .selectbox-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    .recommend-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
    }
    
    .recommend-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .recommendations-header {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin: 3rem 0 2rem 0;
        color: #333;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
    }
    
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def fetch_movie_details(movie_id):
    """Fetch detailed movie information including poster, rating, and overview"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url, timeout=10)
        data = data.json()
        
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            full_path = None
            
        return {
            'poster': full_path,
            'rating': data.get('vote_average', 'N/A'),
            'overview': data.get('overview', 'No description available.'),
            'release_date': data.get('release_date', 'Unknown'),
            'genres': [genre['name'] for genre in data.get('genres', [])]
        }
    except Exception as e:
        st.error(f"Error fetching movie details: {str(e)}")
        return None

def recommend(movie):
    """Get movie recommendations with enhanced error handling"""
    global movies, similarity
    
    if movies is None or similarity is None:
        st.error("Movie data not loaded. Please check your artifacts folder.")
        return []
    
    try:
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_movies = []
        for i in distances[1:6]:
            movie_id = movies.iloc[i[0]].movie_id
            movie_title = movies.iloc[i[0]].title
            movie_details = fetch_movie_details(movie_id)
            
            if movie_details:
                recommended_movies.append({
                    'title': movie_title,
                    'details': movie_details,
                    'similarity_score': distances[i[0]][1]
                })
        
        return recommended_movies
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return []

def main():
    # Check if data is loaded
    if movies is None or similarity is None:
        st.error("Failed to load movie data. Please ensure the artifacts folder contains the required pickle files.")
        return
    
    # Header
    st.markdown('<h1 class="main-header">🎬 Perfect Pitch</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Discover your next favorite movie with AI-powered recommendations</p>', unsafe_allow_html=True)
    
    # Statistics
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-item"><div class="stat-number">{}</div><div class="stat-label">Movies</div></div>'.format(len(movies)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-item"><div class="stat-number">5</div><div class="stat-label">Recommendations</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-item"><div class="stat-number">AI</div><div class="stat-label">Powered</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Movie selection
    st.markdown('<div class="selectbox-container">', unsafe_allow_html=True)
    st.markdown("### 🎯 Select a Movie")
    st.markdown("Choose a movie you love, and we'll find similar ones you might enjoy!")
    
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list,
        index=0 if len(movie_list) > 0 else None,
        help="Start typing to search through our movie database"
    )
    
    if st.button('🎬 Get Recommendations', key='recommend_btn'):
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.spinner('🎭 Finding the perfect movies for you...'):
            recommended_movies = recommend(selected_movie)
        
        if recommended_movies:
            st.markdown('<h2 class="recommendations-header">🎉 Here are your recommendations!</h2>', unsafe_allow_html=True)
            
            # Display recommendations in a grid
            cols = st.columns(5)
            for idx, movie in enumerate(recommended_movies):
                with cols[idx]:
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                    
                    # Movie poster
                    if movie['details']['poster']:
                        st.image(movie['details']['poster'], use_container_width=True, caption="")
                    else:
                        st.image("https://via.placeholder.com/300x450?text=No+Poster", use_container_width=True, caption="")
                    
                    # Movie title
                    st.markdown(f'<div class="movie-title">{movie["title"]}</div>', unsafe_allow_html=True)
                    
                    # Rating
                    if movie['details']['rating'] != 'N/A':
                        st.markdown(f"⭐ **{movie['details']['rating']}/10**")
                    
                    # Similarity score
                    similarity_percent = round(movie['similarity_score'] * 100, 1)
                    st.markdown(f"🎯 **{similarity_percent}%** similar")
                    
                    # Genres
                    if movie['details']['genres']:
                        genres_text = ", ".join(movie['details']['genres'][:3])
                        st.markdown(f"🎭 {genres_text}")
                    
                    # Release date
                    if movie['details']['release_date'] != 'Unknown':
                        st.markdown(f"📅 {movie['details']['release_date'][:4]}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No recommendations found. Please try another movie.")
    else:
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🎬 Perfect Pitch - AI Movie Recommendations</p>
        <p>Powered by Machine Learning & The Movie Database API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
