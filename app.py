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
    # Load the full movies data for detailed information
    full_movies = pickle.load(open('artifacts/full_movies.pkl', 'rb'))
except Exception as e:
    st.error(f"Error loading movie data: {str(e)}")
    movies = None
    similarity = None
    full_movies = None

# Custom CSS for better styling
st.markdown("""
<style>
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
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
    
    .icon {
        margin-right: 8px;
    }
    
    .icon-container {
        display: inline-block;
        margin-right: 8px;
    }
    
    .selected-movie-container {
        background: transparent;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .selected-movie-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: inherit;
    }
    
    .movie-details-grid {
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 2rem;
        align-items: start;
    }
    
    .movie-info-section {
        background: transparent;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 0.5rem;
    }
    
    .info-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 1rem;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    .cast-crew-item {
        background: rgba(255, 255, 255, 0.05);
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        border-radius: 5px;
        border-left: 3px solid #667eea;
        color: inherit;
    }
    
    .overview-text {
        line-height: 1.6;
        color: inherit;
        text-align: justify;
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

def get_selected_movie_details(selected_movie):
    """Get detailed information about the selected movie from our dataset"""
    try:
        # Find the movie in our dataset
        movie_data = full_movies[full_movies['title'] == selected_movie].iloc[0]
        
        # Get poster and additional details from TMDB API
        tmdb_details = fetch_movie_details(movie_data['movie_id'])
        
        # Extract cast, crew, and overview from our dataset
        cast = movie_data['cast']
        crew = movie_data['crew']
        overview = movie_data['overview']
        genres = movie_data['genres']
        production_companies = movie_data['production_companies']
        
        return {
            'title': selected_movie,
            'cast': cast,
            'crew': crew,
            'overview': overview,
            'genres': genres,
            'production_companies': production_companies,
            'tmdb_details': tmdb_details
        }
    except Exception as e:
        st.error(f"Error getting movie details: {str(e)}")
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
    if movies is None or similarity is None or full_movies is None:
        st.error("Failed to load movie data. Please ensure the artifacts folder contains the required pickle files.")
        return
    
    # Header
    st.markdown('<h1 class="main-header"><i class="fas fa-film"></i> Perfect Pitch</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Discover your next favorite movie with AI-powered recommendations</p>', unsafe_allow_html=True)
    
    # Statistics
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-item"><div class="stat-number">{}</div><div class="stat-label"><i class="fas fa-film icon"></i>Movies</div></div>'.format(len(movies)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-item"><div class="stat-number">5</div><div class="stat-label"><i class="fas fa-star icon"></i>Recommendations</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-item"><div class="stat-number">AI</div><div class="stat-label"><i class="fas fa-robot icon"></i>Powered</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Movie selection
    st.markdown('<div class="selectbox-container">', unsafe_allow_html=True)
    st.markdown("### <span class='icon-container'><i class='fas fa-bullseye icon'></i></span>Select a Movie", unsafe_allow_html=True)
    st.markdown("Choose a movie you love, and we'll find similar ones you might enjoy!")
    
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list,
        index=0 if len(movie_list) > 0 else None,
        help="Start typing to search through our movie database"
    )
    
    if st.button('Get Movie Details & Recommendations', key='recommend_btn'):
        st.markdown('</div>', unsafe_allow_html=True)
        
        with st.spinner('Loading movie details and finding recommendations...'):
            # Get selected movie details
            selected_movie_details = get_selected_movie_details(selected_movie)
            # Get recommendations
            recommended_movies = recommend(selected_movie)
        
        if selected_movie_details:
            # Display selected movie details
            st.markdown('<div class="selected-movie-container">', unsafe_allow_html=True)
            st.markdown(f'<h2 class="selected-movie-header"><i class="fas fa-star icon"></i> {selected_movie_details["title"]}</h2>', unsafe_allow_html=True)
            
            # Create a grid layout for movie details
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Movie poster
                if selected_movie_details['tmdb_details'] and selected_movie_details['tmdb_details']['poster']:
                    st.image(selected_movie_details['tmdb_details']['poster'], use_container_width=True, caption="")
                else:
                    st.image("https://via.placeholder.com/300x450?text=No+Poster", use_container_width=True, caption="")
                
                # Basic info
                if selected_movie_details['tmdb_details']:
                    if selected_movie_details['tmdb_details']['rating'] != 'N/A':
                        st.markdown(f"<i class='fas fa-star icon'></i> **Rating: {selected_movie_details['tmdb_details']['rating']}/10**", unsafe_allow_html=True)
                    
                    if selected_movie_details['tmdb_details']['release_date'] != 'Unknown':
                        st.markdown(f"<i class='fas fa-calendar-alt icon'></i> **Released: {selected_movie_details['tmdb_details']['release_date']}**", unsafe_allow_html=True)
            
            with col2:
                # Overview
                st.markdown('<div class="movie-info-section">', unsafe_allow_html=True)
                st.markdown('<div class="info-title"><i class="fas fa-info-circle icon"></i> Overview</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="overview-text">{selected_movie_details["overview"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Cast
                if selected_movie_details['cast']:
                    st.markdown('<div class="movie-info-section">', unsafe_allow_html=True)
                    st.markdown('<div class="info-title"><i class="fas fa-users icon"></i> Cast</div>', unsafe_allow_html=True)
                    for actor in selected_movie_details['cast']:
                        st.markdown(f'<div class="cast-crew-item">{actor}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Crew (Directors)
                if selected_movie_details['crew']:
                    st.markdown('<div class="movie-info-section">', unsafe_allow_html=True)
                    st.markdown('<div class="info-title"><i class="fas fa-video icon"></i> Directors</div>', unsafe_allow_html=True)
                    for director in selected_movie_details['crew']:
                        st.markdown(f'<div class="cast-crew-item">{director}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Genres
                if selected_movie_details['genres']:
                    st.markdown('<div class="movie-info-section">', unsafe_allow_html=True)
                    st.markdown('<div class="info-title"><i class="fas fa-tags icon"></i> Genres</div>', unsafe_allow_html=True)
                    genres_text = ", ".join(selected_movie_details['genres'])
                    st.markdown(f'<div class="overview-text">{genres_text}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if recommended_movies:
            st.markdown('<h2 class="recommendations-header"><i class="fas fa-trophy icon"></i> Related Movies You Might Like</h2>', unsafe_allow_html=True)
            
            # Display recommendations in a grid
            cols = st.columns(5)
            for idx, movie in enumerate(recommended_movies):
                with cols[idx]:
                    # Movie poster
                    if movie['details']['poster']:
                        st.image(movie['details']['poster'], use_container_width=True, caption="")
                    else:
                        st.image("https://via.placeholder.com/300x450?text=No+Poster", use_container_width=True, caption="")
                    
                    # Movie title
                    st.markdown(f'<div class="movie-title">{movie["title"]}</div>', unsafe_allow_html=True)
                    
                    # Rating
                    if movie['details']['rating'] != 'N/A':
                        st.markdown(f"<i class='fas fa-star icon'></i> **{movie['details']['rating']}/10**", unsafe_allow_html=True)
                    
                    # Similarity score
                    similarity_percent = round(movie['similarity_score'] * 100, 1)
                    st.markdown(f"<i class='fas fa-bullseye icon'></i> **{similarity_percent}%** similar", unsafe_allow_html=True)
                    
                    # Genres
                    if movie['details']['genres']:
                        genres_text = ", ".join(movie['details']['genres'][:3])
                        st.markdown(f"<i class='fas fa-tags icon'></i> {genres_text}", unsafe_allow_html=True)
                    
                    # Release date
                    if movie['details']['release_date'] != 'Unknown':
                        st.markdown(f"<i class='fas fa-calendar-alt icon'></i> {movie['details']['release_date'][:4]}", unsafe_allow_html=True)
        else:
            st.warning("No recommendations found. Please try another movie.")
    else:
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><i class="fas fa-film"></i> Perfect Pitch - AI Movie Recommendations</p>
        <p>Powered by Machine Learning & The Movie Database API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()