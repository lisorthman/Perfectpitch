import pandas as pd
import pickle
import ast

def convert_to_names(text):
    """Convert string representation of lists to actual lists of names"""
    try:
        if pd.isna(text):
            return []
        l = []
        for i in ast.literal_eval(text):
            l.append(i['name'])
        return l
    except:
        return []

def convert_cast_to_names(text):
    """Convert cast string to list of actor names (top 5)"""
    try:
        if pd.isna(text):
            return []
        l = []
        counter = 0
        for i in ast.literal_eval(text):
            if counter < 5:  # Get top 5 cast members
                l.append(i['name'])
                counter += 1
        return l
    except:
        return []

def fetch_director(text):
    """Extract only the first director name from crew data"""
    try:
        if pd.isna(text):
            return []
        l = []
        for i in ast.literal_eval(text):
            if i['job'] == 'Director':
                l.append(i['name'])
                break  # Only get the first director
        return l
    except:
        return []

def main():
    print("Loading movie data...")
    
    # Load the original datasets
    movies = pd.read_csv('data/tmdb_5000_movies.csv')
    credits = pd.read_csv('data/tmdb_5000_credits.csv')
    
    print(f"Original movies shape: {movies.shape}")
    print(f"Original credits shape: {credits.shape}")
    
    # Merge the datasets
    movies = movies.merge(credits, on='title')
    print(f"After merge shape: {movies.shape}")
    
    # Select relevant columns for detailed view
    detailed_movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew', 'production_companies']].copy()
    
    # Remove rows with missing data
    detailed_movies.dropna(inplace=True)
    print(f"After removing nulls shape: {detailed_movies.shape}")
    
    # Convert string representations to clean lists for display
    print("Converting data formats for display...")
    detailed_movies['genres'] = detailed_movies['genres'].apply(convert_to_names)
    detailed_movies['production_companies'] = detailed_movies['production_companies'].apply(convert_to_names)
    detailed_movies['keywords'] = detailed_movies['keywords'].apply(convert_to_names)
    detailed_movies['cast'] = detailed_movies['cast'].apply(convert_cast_to_names)
    detailed_movies['crew'] = detailed_movies['crew'].apply(fetch_director)
    
    # Keep overview as original text (don't split into words)
    
    print("Sample of processed data:")
    print(detailed_movies.head(2))
    
    # Save the detailed movies data
    print("Saving full_movies.pkl...")
    pickle.dump(detailed_movies, open('artifacts/full_movies.pkl', 'wb'))
    
    print("Successfully created full_movies.pkl!")
    print(f"Final shape: {detailed_movies.shape}")
    
    # Show sample data
    print("\nSample movie details:")
    sample_movie = detailed_movies.iloc[0]
    print(f"Title: {sample_movie['title']}")
    print(f"Cast: {sample_movie['cast']}")
    print(f"Director: {sample_movie['crew']}")
    print(f"Genres: {sample_movie['genres']}")
    print(f"Overview: {sample_movie['overview'][:100]}...")

if __name__ == "__main__":
    main()
