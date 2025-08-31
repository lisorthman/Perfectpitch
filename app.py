import pickle
import streamlit as st
import requests
import pandas as pd
from PIL import Image
import io
import joblib
import re

# Page configuration
st.set_page_config(
    page_title="PerfectPitch - Movie Recommender",
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
    # Load sentiment analysis model and vectorizer
    sentiment_model = joblib.load('artifacts/sentiment_model.pkl')
    tfidf_vectorizer = joblib.load('artifacts/tfidf_vectorizer.pkl')
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    movies = None
    similarity = None
    full_movies = None
    sentiment_model = None
    tfidf_vectorizer = None

# Add this CSS after your imports for a futuristic sci-fi theme

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Exo+2:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(to bottom, #000428, #004e92);
        color: #FFFFFF;
        font-family: 'Exo 2', sans-serif;
    }
    
    .main-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        color: #00F3FF;
        margin-bottom: 1rem;
        text-shadow: 0px 0px 15px rgba(0, 243, 255, 0.7);
        letter-spacing: 2px;
    }
    
    .subtitle {
        text-align: center;
        color: #8BE9FD;
        font-size: 1.3rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    .movie-card {
        background: rgba(0, 10, 30, 0.7);
        border-radius: 8px;
        padding: 15px;
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 243, 255, 0.3);
        height: 100%;
        backdrop-filter: blur(5px);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(0, 243, 255, 0.6);
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
    }
    
    .movie-title {
        font-weight: 600;
        font-size: 1rem;
        margin: 0.5rem 0;
        color: #FFFFFF;
        text-align: center;
        line-height: 1.3;
        height: 2.6rem;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
    
    .movie-poster {
        border-radius: 4px;
        width: 100%;
        height: auto;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(0, 243, 255, 0.2);
    }
    
    .movie-poster:hover {
        transform: scale(1.03);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
    }
    
    .stSelectbox > div > div {
        background-color: rgba(0, 10, 30, 0.7);
        color: #FFFFFF;
        border: 1px solid rgba(0, 243, 255, 0.3);
        border-radius: 4px;
    }
    
    .stSelectbox label {
        color: #00F3FF !important;
        font-weight: 600;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00F3FF 0%, #0288D1 100%);
        color: #000C1D;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 4px;
        font-size: 1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.5);
    }
    
    .stTextArea > div > div > textarea {
        background-color: rgba(0, 10, 30, 0.7);
        color: #FFFFFF;
        border: 1px solid rgba(0, 243, 255, 0.3);
    }
    
    .section-header {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 2rem 0 1.5rem 0;
        color: #00F3FF;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00F3FF;
        display: inline-block;
        text-shadow: 0px 0px 10px rgba(0, 243, 255, 0.5);
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        padding: 1.5rem;
        background: rgba(0, 10, 30, 0.7);
        border-radius: 8px;
        color: #FFFFFF;
        border: 1px solid rgba(0, 243, 255, 0.3);
        backdrop-filter: blur(5px);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.2rem;
        font-weight: bold;
        color: #00F3FF;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0px 0px 10px rgba(0, 243, 255, 0.5);
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #8BE9FD;
    }
    
    .rating-stars {
        color: #00F3FF;
        font-size: 1.2rem;
        margin: 0.5rem 0;
        text-shadow: 0px 0px 5px rgba(0, 243, 255, 0.5);
    }
    
    .similarity-meter {
        height: 8px;
        background: rgba(0, 243, 255, 0.2);
        border-radius: 4px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .similarity-fill {
        height: 100%;
        background: linear-gradient(90deg, #00F3FF 0%, #0288D1 100%);
        border-radius: 4px;
    }
    
    .review-container {
        background: rgba(0, 10, 30, 0.7);
        padding: 2rem;
        border-radius: 8px;
        margin: 2rem 0;
        border: 1px solid rgba(0, 243, 255, 0.3);
        backdrop-filter: blur(5px);
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.1);
    }
    
    .footer {
        text-align: center;
        color: #8BE9FD;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid rgba(0, 243, 255, 0.3);
    }
    
    .neon-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #00F3FF, transparent);
        margin: 2rem 0;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
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

def analyze_sentiment(review_text):
    """Analyze the sentiment of a movie review"""
    try:
        if sentiment_model is None or tfidf_vectorizer is None:
            return None, "Model not loaded"
        
        # Clean the text
        cleaned_text = re.sub(r'[^\w\s]', '', review_text.lower())
        
        # Transform the text using the loaded vectorizer
        text_features = tfidf_vectorizer.transform([cleaned_text])
        
        # Make prediction
        prediction = sentiment_model.predict(text_features)[0]
        probability = sentiment_model.predict_proba(text_features)[0]
        
        # Get confidence score
        confidence = max(probability)
        
        sentiment_label = "Positive" if prediction == 1 else "Negative"
        
        return {
            'sentiment': sentiment_label,
            'confidence': confidence,
            'prediction': prediction
        }
    except Exception as e:
        return None, str(e)

def display_rating_stars(rating):
    """Display rating as stars"""
    if rating == 'N/A':
        return "No rating"
    
    full_stars = int(float(rating) / 2)
    half_star = 1 if (float(rating) / 2 - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    stars_html = ""
    for _ in range(full_stars):
        stars_html += '<i class="fas fa-star"></i>'
    for _ in range(half_star):
        stars_html += '<i class="fas fa-star-half-alt"></i>'
    for _ in range(empty_stars):
        stars_html += '<i class="far fa-star"></i>'
    
    return f'<div class="rating-stars">{stars_html} {rating}/10</div>'

def main():
    # Check if data is loaded
    if movies is None or similarity is None or full_movies is None:
        st.error("Failed to load movie data. Please ensure the artifacts folder contains the required pickle files.")
        return
    
    # Header with cinematic style
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 class="main-header"><i class="fas fa-film"></i> PerfectPitch</h1>
        <p class="subtitle">Your Personal Movie Connoisseur</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistics Banner
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-item"><div class="stat-number">{}</div><div class="stat-label"><i class="fas fa-film icon"></i>Movies</div></div>'.format(len(movies)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-item"><div class="stat-number">5</div><div class="stat-label"><i class="fas fa-ticket-alt icon"></i>Recommendations</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-item"><div class="stat-number">88.9%</div><div class="stat-label"><i class="fas fa-robot icon"></i>AI Accuracy</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-item"><div class="stat-number">50K</div><div class="stat-label"><i class="fas fa-database icon"></i>Reviews</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 1: Movie Recommendations
    st.markdown("---")
    st.markdown('<h2 class="section-header"><i class="fas fa-clapperboard"></i> Movie Recommendations</h2>', unsafe_allow_html=True)
    st.markdown("Discover similar movies based on your favorites")
    
    # Movie selection with improved styling
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "🎭 Choose a movie you love:",
        movie_list,
        index=0 if len(movie_list) > 0 else None,
        help="Start typing to search through our movie database"
    )
    
    # Get recommendations button
    if st.button('🎬 Get Movie Recommendations', key='recommend_btn', use_container_width=True):
        with st.spinner('Finding the perfect matches...'):
            # Get selected movie details
            selected_movie_details = get_selected_movie_details(selected_movie)
            # Get recommendations
            recommended_movies = recommend(selected_movie)
            
            # Store in session state to preserve after other actions
            st.session_state.selected_movie_details = selected_movie_details
            st.session_state.recommended_movies = recommended_movies
    
    # Display recommendations (will be preserved)
    if 'selected_movie_details' in st.session_state and st.session_state.selected_movie_details:
        # Display selected movie details
        st.markdown("### 🎬 Selected Movie Details")
        
        # Create a grid layout for movie details
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Movie poster
            if st.session_state.selected_movie_details['tmdb_details'] and st.session_state.selected_movie_details['tmdb_details']['poster']:
                st.image(st.session_state.selected_movie_details['tmdb_details']['poster'], use_container_width=True, caption="")
            else:
                st.image("https://via.placeholder.com/300x450?text=No+Poster", use_container_width=True, caption="")
            
            # Basic info
            if st.session_state.selected_movie_details['tmdb_details']:
                if st.session_state.selected_movie_details['tmdb_details']['rating'] != 'N/A':
                    st.markdown(display_rating_stars(st.session_state.selected_movie_details['tmdb_details']['rating']), unsafe_allow_html=True)
                
                if st.session_state.selected_movie_details['tmdb_details']['release_date'] != 'Unknown':
                    st.markdown(f"📅 **Released: {st.session_state.selected_movie_details['tmdb_details']['release_date']}**")
        
        with col2:
            # Overview
            st.markdown("**📖 Overview:**")
            st.markdown(f"<div class='overview-text'>{st.session_state.selected_movie_details['overview']}</div>", unsafe_allow_html=True)
            
            # Cast
            if st.session_state.selected_movie_details['cast']:
                st.markdown("**👥 Cast:**")
                cast_text = ", ".join(st.session_state.selected_movie_details['cast'][:5])  # Show first 5
                st.markdown(cast_text)
            
            # Genres
            if st.session_state.selected_movie_details['genres']:
                st.markdown("**🏷️ Genres:**")
                genres_text = ", ".join(st.session_state.selected_movie_details['genres'])
                st.markdown(genres_text)
    
    if 'recommended_movies' in st.session_state and st.session_state.recommended_movies:
        st.markdown("---")
        st.markdown("### 🎯 Recommended Movies")
        
        # Display recommendations in a grid with movie cards
        cols = st.columns(5)
        for idx, movie in enumerate(st.session_state.recommended_movies):
            with cols[idx]:
                # Create movie card
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
                    st.markdown(display_rating_stars(movie['details']['rating']), unsafe_allow_html=True)
                
                # Similarity score with visual meter
                similarity_percent = round(movie['similarity_score'] * 100, 1)
                st.markdown(f"**Match: {similarity_percent}%**")
                st.markdown(f'<div class="similarity-meter"><div class="similarity-fill" style="width: {similarity_percent}%"></div></div>', unsafe_allow_html=True)
                
                # Genres
                if movie['details']['genres']:
                    genres_text = ", ".join(movie['details']['genres'][:2])
                    st.markdown(f"🏷️ {genres_text}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 2: Review This Movie
    st.markdown("---")
    st.markdown('<h2 class="section-header"><i class="fas fa-pen"></i> Review This Movie</h2>', unsafe_allow_html=True)
    st.markdown(f"Share your thoughts about **{selected_movie}**")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Review text area
        movie_review = st.text_area(
            "Your review:",
            value=st.session_state.get('sample_review', ''),
            placeholder=f"Write your review about {selected_movie}...",
            height=120,
            key="movie_review"
        )
        
        # Review analysis button
        if st.button("🔍 Analyze My Review", key="movie_review_btn", use_container_width=True):
            if movie_review.strip():
                with st.spinner("Analyzing your movie review..."):
                    result = analyze_sentiment(movie_review)
                
                if isinstance(result, dict):
                    st.markdown("### 📊 Review Analysis Results")
                    
                    # Display results
                    result_col1, result_col2 = st.columns([1, 1])
                    
                    with result_col1:
                        if result['sentiment'] == 'Positive':
                            st.success(f"😊 **Positive Sentiment**")
                        else:
                            st.error(f"😞 **Negative Sentiment**")
                        
                        confidence_percent = round(result['confidence'] * 100, 1)
                        st.metric("Confidence Score", f"{confidence_percent}%")
                    
                    with result_col2:
                        if result['sentiment'] == 'Positive':
                            st.success(f"🎉 **Great choice!** You really enjoyed {selected_movie}!")
                        else:
                            st.warning(f"📝 **Honest feedback!** Your review of {selected_movie} provides valuable insights.")
                    
                    # Analysis details
                    st.info(f"**AI Analysis:** The model predicts this review as **{result['sentiment'].lower()}** with {confidence_percent}% confidence.")
                else:
                    st.error(f"Error analyzing sentiment: {result}")
            else:
                st.warning("Please write a review to analyze.")
    
    with col2:
        # Sample reviews section
        st.markdown("### 💡 Try Sample Reviews")
        st.markdown("Click any sample to test the system:")
        
        sample_reviews = [
            "This movie was absolutely amazing! I loved every minute of it.",
            "Terrible film, waste of time and money.",
            "The acting was good but the plot was confusing.",
            "A masterpiece that will be remembered for generations."
        ]
        
        for i, sample in enumerate(sample_reviews):
            if st.button(f"Sample {i+1}: {sample[:25]}...", key=f"sample_{i}"):
                st.session_state.sample_review = sample
                st.rerun()
        
        # Clear button
        if st.button("🗑️ Clear Review", key="clear_review"):
            st.session_state.sample_review = ""
            st.rerun()
    
    # About Section
    st.markdown("---")
    st.markdown('<h2 class="section-header"><i class="fas fa-info-circle"></i> About PerfectPitch</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 What We Do")
        st.markdown("""
        **PerfectPitch** is an AI-powered movie analysis and recommendation system that:
        
        - 🧠 Analyzes movie review sentiment with 88.9% accuracy
        - 🎬 Recommends similar movies using content-based filtering
        - 📝 Provides personalized movie insights
        - 🚀 Uses machine learning for intelligent suggestions
        """)
    
    with col2:
        st.markdown("### 📈 Model Performance")
        st.markdown("""
        **Sentiment Analysis Model:**
        - **Accuracy**: 88.9%
        - **Training Data**: 50,000 IMDB reviews
        - **Model**: Logistic Regression + TF-IDF
        - **Features**: 5,000 max features
        
        **Recommendation System:**
        - **Algorithm**: Cosine Similarity
        - **Features**: Genres, tags, keywords
        - **Output**: Top 5 similar movies
        """)
    
    st.markdown("---")
    st.markdown("### 🛠️ Technical Stack")
    st.markdown("""
    - **Frontend**: Streamlit
    - **ML Framework**: Scikit-learn
    - **Data Processing**: Pandas, NumPy
    - **Text Analysis**: TF-IDF Vectorization
    - **Similarity**: Cosine Similarity Algorithm
    """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p><i class="fas fa-film"></i> PerfectPitch - AI Movie Analysis & Recommendations</p>
        <p>Powered by Machine Learning & The Movie Database API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()