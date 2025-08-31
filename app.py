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

def main():
    # Check if data is loaded
    if movies is None or similarity is None or full_movies is None:
        st.error("Failed to load movie data. Please ensure the artifacts folder contains the required pickle files.")
        return
    
    # Header
    st.markdown('<h1 class="main-header"><i class="fas fa-film"></i> Perfect Pitch</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">AI-Powered Movie Analysis & Recommendations</p>', unsafe_allow_html=True)
    
    # Statistics Banner
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="stat-item"><div class="stat-number">{}</div><div class="stat-label"><i class="fas fa-film icon"></i>Movies</div></div>'.format(len(movies)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stat-item"><div class="stat-number">5</div><div class="stat-label"><i class="fas fa-star icon"></i>Recommendations</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stat-item"><div class="stat-number">88.9%</div><div class="stat-label"><i class="fas fa-robot icon"></i>AI Accuracy</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stat-item"><div class="stat-number">50K</div><div class="stat-label"><i class="fas fa-database icon"></i>Reviews</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section 1: Movie Recommendations (FIRST)
    st.markdown("---")
    st.markdown("## 🎬 **Movie Recommendations**")
    st.markdown("Discover similar movies based on your favorites")
    
    # Movie selection
    st.markdown("### Select a Movie")
    movie_list = movies['title'].values
    selected_movie = st.selectbox(
        "Choose a movie you love:",
        movie_list,
        index=0 if len(movie_list) > 0 else None,
        help="Start typing to search through our movie database"
    )
    
    # Get recommendations button
    if st.button('🎯 Get Movie Recommendations', key='recommend_btn', type="primary", use_container_width=True):
        with st.spinner('Finding similar movies...'):
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
                    st.markdown(f"⭐ **Rating: {st.session_state.selected_movie_details['tmdb_details']['rating']}/10**")
                
                if st.session_state.selected_movie_details['tmdb_details']['release_date'] != 'Unknown':
                    st.markdown(f"📅 **Released: {st.session_state.selected_movie_details['tmdb_details']['release_date']}**")
        
        with col2:
            # Overview
            st.markdown("**📖 Overview:**")
            st.markdown(f"{st.session_state.selected_movie_details['overview']}")
            
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
        
        # Display recommendations in a grid
        cols = st.columns(5)
        for idx, movie in enumerate(st.session_state.recommended_movies):
            with cols[idx]:
                # Movie poster
                if movie['details']['poster']:
                    st.image(movie['details']['poster'], use_container_width=True, caption="")
                else:
                    st.image("https://via.placeholder.com/300x450?text=No+Poster", use_container_width=True, caption="")
                
                # Movie title
                st.markdown(f'**{movie["title"]}**')
                
                # Rating
                if movie['details']['rating'] != 'N/A':
                    st.markdown(f"⭐ {movie['details']['rating']}/10")
                
                # Similarity score
                similarity_percent = round(movie['similarity_score'] * 100, 1)
                st.markdown(f"🎯 {similarity_percent}% similar")
                
                # Genres
                if movie['details']['genres']:
                    genres_text = ", ".join(movie['details']['genres'][:2])
                    st.markdown(f"🏷️ {genres_text}")
    
        # Section 2: Review This Movie
    st.markdown("---")
    st.markdown("## 📝 **Review This Movie**")
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
        if st.button("🔍 Analyze My Review", key="movie_review_btn", use_container_width=True, type="primary"):
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
    st.markdown("## 📊 **About Perfect Pitch**")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 What We Do")
        st.markdown("""
        **Perfect Pitch** is an AI-powered movie analysis and recommendation system that:
        
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
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p><i class="fas fa-film"></i> Perfect Pitch - AI Movie Analysis & Recommendations</p>
        <p>Powered by Machine Learning & The Movie Database API</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()