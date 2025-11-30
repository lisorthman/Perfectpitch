
# 🎬 Perfect Pitch - Movie Recommender System Using Machine Learning

## Overview

This project is a **Movie Recommendation System** built with **Python** and **Machine Learning**.
It recommends movies similar to a selected movie based on **tags, genres, and keywords**.
The system uses **Count Vectorizer** and **Cosine Similarity** to find movies with similar content.

**NEW!** 🧠 **AI Sentiment Analysis** - Analyze movie review sentiment with 88.9% accuracy!

---

## Features

* Recommend top 5 movies similar to the selected movie.
* Uses **cosine similarity** for accurate recommendations.
* Preprocessed movie tags for better matching using **stemming**.
* Interactive **Streamlit app** for easy usage.
* **AI Sentiment Analysis** for movie reviews (Positive/Negative classification).
* **Confidence scoring** for sentiment predictions.
* **Sample review testing** with pre-built examples.
* Lightweight and easy to deploy.

---

## Folder Structure

```
Perfectpitch/
│── artifacts/           # Pickle files for movie list, similarity matrix & ML models
│   ├── movie_list.pkl
│   ├── similarity.pkl
│   ├── full_movies.pkl
│   ├── sentiment_model.pkl      # Sentiment analysis model
│   └── tfidf_vectorizer.pkl    # Text vectorizer for sentiment analysis
│── data/                # Original dataset CSV (optional)
│── env/                 # Conda environment (optional)
│── src/                 # Python package with source code
│   ├── __init__.py
│   ├── app.py           # Streamlit app / main script
│   └── utils.py         # Recommendation logic
│── README.md
│── setup.py             # Package configuration
│── requirements.txt     # Project dependencies
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/lisorthman/Perfectpitch
cd Perfectpitch
```

### 2. Create a Conda environment

```bash
conda create --prefix ./env python=3.10 -y
conda activate ./env
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Docker Deployment 🐳

### Prerequisites

* Docker installed on your system ([Get Docker](https://docs.docker.com/get-docker/))
* Docker Compose (included with Docker Desktop)

### Option 1: Using Docker Compose (Recommended)

The easiest way to run the application:

```bash
# Navigate to project directory
cd Perfectpitch

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

Access the application at: **http://localhost:8501**

### Option 2: Using Docker CLI

Build and run manually:

```bash
# Build the Docker image
docker build -t perfectpitch:latest .

# Run the container
docker run -d -p 8501:8501 --name perfectpitch perfectpitch:latest

# View logs
docker logs -f perfectpitch

# Stop and remove container
docker stop perfectpitch
docker rm perfectpitch
```

### Docker Configuration

**Port Mapping**: The application runs on port `8501` inside the container and is mapped to `8501` on your host machine.

**Volume Mounting** (Optional): To update artifacts without rebuilding:
```bash
docker run -d -p 8501:8501 -v $(pwd)/artifacts:/app/artifacts:ro perfectpitch:latest
```

**Environment Variables**: Currently no environment variables required.

### Troubleshooting

* **Port already in use**: Change the host port mapping: `-p 8080:8501`
* **Container won't start**: Check logs with `docker logs perfectpitch`
* **Out of memory**: The artifacts are ~188MB, ensure Docker has sufficient memory allocated

---

## Local Development

### Prerequisites

* Python >= 3.7
* Conda (recommended) or virtualenv

### Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/lisorthman/Perfectpitch
cd Perfectpitch
```

### 2. Create a Conda environment

```bash
conda create --prefix ./env python=3.10 -y
conda activate ./env
```

### 3. Install dependencies

```bash
pip install -r requirements.txt


### Run the Streamlit app

```bash
streamlit run app.py
```

### Movie Recommendations
* Select a movie from the dropdown.
* Click **"Get Movie Details & Recommendations"**.
* View the **top 5 recommended movies** instantly.

### Sentiment Analysis
* **Top Section**: Test sentiment analysis with any movie review text.
* Get instant **Positive/Negative** classification.
* View **confidence scores** for predictions.
* Try **sample reviews** to test the system.

### Movie Review Writing
* **Below Movie Selection**: Write reviews about selected movies.
* Get **personalized sentiment analysis** for your movie reviews.
* Analyze your writing style and sentiment.

---

## How it works

### Movie Recommendations
1. Movie dataset is preprocessed:
   * Tags are lowercased and stemmed using **PorterStemmer**.
2. Text is converted into vectors using **CountVectorizer**.
3. **Cosine Similarity** is calculated between movies.
4. Recommendations are generated based on the most similar movies.

### Sentiment Analysis
1. **TF-IDF Vectorization** converts review text to numerical features.
2. **Logistic Regression** model classifies sentiment (Positive/Negative).
3. **Confidence scoring** provides prediction reliability.
4. **Text preprocessing** ensures consistent analysis.

---

## Dependencies

* Python >= 3.7
* pandas
* numpy
* scikit-learn
* nltk
* streamlit
* joblib (for ML model loading)

---

## Model Performance

* **Sentiment Analysis Accuracy**: 88.9% on IMDB movie reviews dataset
* **Training Data**: 50,000 movie reviews (25,000 positive, 25,000 negative)
* **Model**: Logistic Regression with TF-IDF features
* **Vectorizer**: TF-IDF with 5,000 max features and English stop words

---

## Future Enhancements

* Multi-class sentiment analysis (Very Positive, Positive, Neutral, Negative, Very Negative)
* Emotion detection in reviews
* Review summarization
* Sentiment-based movie filtering
* User review sentiment tracking


