
# 🎬 Perfect Pitch - Movie Recommender System Using Machine Learning

## Overview

This project is a **Movie Recommendation System** built with **Python** and **Machine Learning**.
It recommends movies similar to a selected movie based on **tags, genres, and keywords**.
The system uses **Count Vectorizer** and **Cosine Similarity** to find movies with similar content.

---

## Features

* Recommend top 5 movies similar to the selected movie.
* Uses **cosine similarity** for accurate recommendations.
* Preprocessed movie tags for better matching using **stemming**.
* Interactive **Streamlit app** for easy usage.
* Lightweight and easy to deploy.

---

## Folder Structure

```
Perfectpitch/
│── artifacts/           # Pickle files for movie list & similarity matrix
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

## Usage

### Run the Streamlit app

```bash
streamlit run src/app.py
```

* Select a movie from the dropdown.
* Click **“Recommend”**.
* View the **top 5 recommended movies** instantly.

---

## How it works

1. Movie dataset is preprocessed:

   * Tags are lowercased and stemmed using **PorterStemmer**.
2. Text is converted into vectors using **CountVectorizer** or **TF-IDF Vectorizer**.
3. **Cosine Similarity** is calculated between movies.
4. Recommendations are generated based on the most similar movies.

---

## Dependencies

* Python >= 3.7
* pandas
* numpy
* scikit-learn
* nltk
* streamlit

---


