"""
src/recommend.py
────────────────
Core recommendation logic.
Loads the trained model (recommender.pkl) and returns top-5 similar movies.
"""

import os
import pickle
import joblib
import pandas as pd
import numpy as np


# ── paths ──────────────────────────────────────────────────────────────────────
ROOT_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT_DIR, "model", "recommender.pkl")
DATA_PATH  = os.path.join(ROOT_DIR, "data", "movies.csv")


# ── model loading ──────────────────────────────────────────────────────────────
def load_model() -> dict | None:
    """
    Load the trained recommendation model from model/recommender.pkl.

    Expected pickle format (dict):
        {
            "movies":      pd.DataFrame  or  list[str],  # movie titles
            "similarity":  np.ndarray,                   # cosine-similarity matrix
        }

    Returns None if the file is not found.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"[WARN] Model file not found at: {MODEL_PATH}")
        return _fallback_from_csv()

    try:
        # Try joblib first (handles large numpy arrays better)
        model_data = joblib.load(MODEL_PATH)
        print("[INFO] Model loaded via joblib.")
        return model_data
    except Exception:
        pass

    try:
        with open(MODEL_PATH, "rb") as f:
            model_data = pickle.load(f)
        print("[INFO] Model loaded via pickle.")
        return model_data
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return None


def _fallback_from_csv() -> dict | None:
    """
    If the model file is absent but movies.csv exists, build a lightweight
    demo model using TF-IDF on the 'genres' column so the app can still run.
    """
    if not os.path.exists(DATA_PATH):
        return None

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        df = pd.read_csv(DATA_PATH)

        # Expect at minimum a 'title' column; optionally 'genres' / 'overview'
        text_col = next(
            (c for c in ["genres", "overview", "tags"] if c in df.columns), None
        )

        if text_col:
            tfidf = TfidfVectorizer(stop_words="english")
            matrix = tfidf.fit_transform(df[text_col].fillna(""))
            sim    = cosine_similarity(matrix)
        else:
            # No text column → random similarity (pure demo)
            n   = len(df)
            sim = np.random.rand(n, n)
            np.fill_diagonal(sim, 1.0)

        print("[INFO] Fallback model built from movies.csv.")
        return {"movies": df, "similarity": sim}

    except Exception as e:
        print(f"[ERROR] Fallback model failed: {e}")
        return None


# ── helpers ────────────────────────────────────────────────────────────────────
def get_movie_list(model_data: dict) -> list[str]:
    """
    Return a sorted list of all movie titles from the loaded model data.

    model_data["movies"] can be:
        • pd.DataFrame  with a 'title' column
        • list / pd.Series of title strings
    """
    movies = model_data.get("movies")

    if movies is None:
        return []

    if isinstance(movies, pd.DataFrame):
        col = next((c for c in ["title", "Title", "movie", "name"] if c in movies.columns), None)
        if col:
            return sorted(movies[col].dropna().tolist())
        # No recognised column — use index
        return [str(i) for i in movies.index]

    # list / Series / ndarray
    return sorted([str(m) for m in movies])


# ── main API ───────────────────────────────────────────────────────────────────
def recommend(movie_name: str, model_data: dict, top_n: int = 5) -> list[str]:
    """
    Return the top *top_n* movies most similar to *movie_name*.

    Parameters
    ----------
    movie_name : str
        Title of the reference movie.
    model_data : dict
        Dict containing 'movies' and 'similarity' as returned by load_model().
    top_n : int
        Number of recommendations to return (default 5).

    Returns
    -------
    list[str]  — recommended movie titles (empty list on failure)
    """
    movies     = model_data.get("movies")
    similarity = model_data.get("similarity")

    if movies is None or similarity is None:
        print("[ERROR] model_data missing 'movies' or 'similarity' key.")
        return []

    # ── resolve titles list & index ────────────────────────────────────────────
    if isinstance(movies, pd.DataFrame):
        col = next((c for c in ["title", "Title", "movie", "name"] if c in movies.columns), None)
        titles = movies[col].tolist() if col else list(range(len(movies)))
    else:
        titles = list(movies)

    # case-insensitive lookup
    titles_lower = [str(t).lower() for t in titles]
    try:
        idx = titles_lower.index(movie_name.lower())
    except ValueError:
        print(f"[WARN] '{movie_name}' not found in movie list.")
        return []

    # ── sort by similarity ─────────────────────────────────────────────────────
    sim_scores = list(enumerate(similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # skip the movie itself (index 0 after sorting)
    top_indices = [i for i, _ in sim_scores[1 : top_n + 1]]

    return [str(titles[i]) for i in top_indices]

# Mood → genres mapping
MOOD_GENRES = {
    "😂 Comedy / Fun":       ["comedy", "animation", "family"],
    "😱 Thrilling / Suspense": ["thriller", "horror", "mystery"],
    "😢 Emotional / Sad":    ["drama", "biography", "history"],
    "❤️ Romantic":           ["romance"],
    "💥 Action / Hype":      ["action", "adventure", "war"],
    "🧠 Mind-bending":       ["sci-fi", "fantasy", "crime"],
}


def filter_by_genre_and_mood(
    recommendations: list[str],
    model_data: dict,
    selected_genres: list[str],
    selected_moods: list[str],
) -> list[str]:
    """
    Filter a list of recommended movie titles by selected genres and/or moods.
    Returns filtered list — or original list if nothing matches (fallback).
    """
    if not selected_genres and not selected_moods:
        return recommendations

    # Build combined set of genres to match
    genres_to_match = set(g.lower() for g in selected_genres)
    for mood in selected_moods:
        genres_to_match.update(MOOD_GENRES.get(mood, []))

    movies = model_data.get("movies")
    if movies is None or not isinstance(movies, pd.DataFrame):
        return recommendations

    # Find genres column
    genre_col = next(
        (c for c in ["genres", "genre", "Genres"] if c in movies.columns), None
    )
    if not genre_col:
        return recommendations

    # Find title column
    title_col = next(
        (c for c in ["title", "Title", "movie", "name"] if c in movies.columns), None
    )
    if not title_col:
        return recommendations

    filtered = []
    for title in recommendations:
        row = movies[movies[title_col].str.lower() == title.lower()]
        if row.empty:
            continue
        movie_genres = str(row.iloc[0][genre_col]).lower()
        if any(g in movie_genres for g in genres_to_match):
            filtered.append(title)

    # Fallback — return original if filter removes everything
    return filtered if filtered else recommendations