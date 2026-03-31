"""
Movie Recommendation System — Streamlit Frontend (Light Theme)
Run: streamlit run app.py
"""

import streamlit as st
import os
import sys
import requests
from PIL import Image
from io import BytesIO

# ── path setup ────────────────────────────────────────────────────────────────
sys.path.append(os.path.dirname(__file__))

from src.recommend import load_model, get_movie_list, recommend
from src.utils import get_movie_details

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch · Movie Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── custom CSS (light theme) ───────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,700;0,900;1,700&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"], section[data-testid="stMain"], .main {
        background: #f7f5f2 !important;
        color: #1a1a2e !important;
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stHeader"]  { background: transparent !important; }
    [data-testid="stSidebar"] { background: #efefeb !important; }
    .block-container { padding: 0 3rem 4rem !important; max-width: 1280px !important; }

    /* ── navbar ── */
    .navbar { display: flex; align-items: center; justify-content: space-between; padding: 1.2rem 0; border-bottom: 1px solid #e2ddd8; margin-bottom: 0; }
    .nav-logo { font-family: 'Fraunces', serif; font-size: 1.5rem; font-weight: 900; color: #1a1a2e; letter-spacing: -0.02em; }
    .nav-logo span { color: #e05c2a; }
    .nav-tag { font-size: 0.68rem; letter-spacing: 0.2em; text-transform: uppercase; color: #b5a898; }

    /* ── movie card ── */
    .movie-card { background: #fff; border: 1px solid #e8e4de; border-radius: 14px; overflow: hidden; transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease; margin-bottom: 0.5rem; }
    .movie-card:hover { transform: translateY(-6px); box-shadow: 0 20px 50px rgba(26,26,46,0.10); border-color: #e05c2a; }

    .card-rank-bar { padding: 0.55rem 1rem 0; display: flex; align-items: center; gap: 0.4rem; }
    .rank-dot { width: 7px; height: 7px; background: #e05c2a; border-radius: 50%; flex-shrink: 0; }
    .rank-text { font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase; color: #e05c2a; font-weight: 600; }

    .card-body { padding: 0.65rem 1rem 1.1rem; }
    .card-title { font-family: 'Fraunces', serif; font-size: 0.97rem; font-weight: 700; color: #1a1a2e; line-height: 1.3; margin-bottom: 0.45rem; }
    .card-meta { display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; margin-bottom: 0.55rem; }
    .badge-rating { background: #fff8f5; border: 1px solid #f5cbb7; color: #c0440a; font-size: 0.68rem; font-weight: 600; padding: 0.18em 0.65em; border-radius: 999px; }
    .badge-year { color: #b5a898; font-size: 0.72rem; }
    .card-plot { font-size: 0.76rem; color: #7a7060; line-height: 1.55; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }

    .poster-ph { width: 100%; aspect-ratio: 2 / 3; background: linear-gradient(160deg, #f0ece6, #e8e4de); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.5rem; color: #c8bfb0; font-size: 2.8rem; }
    .poster-ph small { font-size: 0.72rem; font-family: 'Inter', sans-serif; color: #c8bfb0; letter-spacing: 0.05em; }

    div[data-testid="stImage"] { margin: 0 !important; padding: 0 !important; line-height: 0; }
    div[data-testid="stImage"] img { border-radius: 0 !important; display: block !important; width: 100% !important; max-height: 340px; object-fit: cover; }

    .stSpinner > div { border-top-color: #e05c2a !important; }
    .stAlert { border-radius: 10px !important; }

    .footer { text-align: center; color: #c0b8ae; font-size: 0.73rem; margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid #e2ddd8; letter-spacing: 0.04em; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── helper to fetch posters ───────────────────────────────────────────────────
def fetch_poster(url: str):
    if not url or url in ("N/A", ""):
        return None
    cache = st.session_state.setdefault("img_cache", {})
    if url in cache:
        return cache[url]
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGB")
        cache[url] = img
        return img
    except Exception:
        return None

# ── navbar ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="navbar">
        <div class="nav-logo">Cine<span>Match</span></div>
        <div class="nav-tag">AI · Movie Recommendations</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── hero section ─────────────────────────────────────────────────────────────
hero_url = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba"
st.markdown(
    f"""
    <div style="
        position: relative;
        text-align: center;
        color: white;
        height: 420px;
        background: url('{hero_url}') center/cover no-repeat;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    ">
        <div style="
            position: absolute;
            inset: 0;
            background: linear-gradient(
                90deg,
                rgba(0,0,0,0.85) 0%,
                rgba(0,0,0,0.55) 45%,
                rgba(0,0,0,0.2) 100%
            );
        "></div>
        <div style="position: relative; z-index: 2;">
            <div style="
                display: inline-block;
                background: #fdf0ea;
                color: #e05c2a;
                padding: 0.32em 1em;
                border-radius: 999px;
                font-size: 0.7rem;
                margin-bottom: 1.4rem;
                text-transform: uppercase;
            ">✦ Powered by Machine Learning</div>
            <h1 style="font-family: 'Fraunces', serif; font-size: 3.5rem; margin: 0;">
                Find your next<br><em style="color:#e05c2a;">favourite film.</em>
            </h1>
            <p style="font-size: 1.1rem; max-width: 480px; margin: 1rem auto 0;">
                Pick a movie you love — we'll recommend five more you're sure to enjoy.
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ── load model ────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_resources():
    return load_model()

with st.spinner("Loading recommendation engine…"):
    model_data = load_resources()

if model_data is None:
    st.error(
        "⚠️ **Model not found.** Export `recommender.pkl` from Google Colab "
        "and place it in the `model/` folder. See README.md for full instructions."
    )
    st.stop()

movies = get_movie_list(model_data)

# ── OMDb API key ──────────────────────────────────────────────────────────────
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "c009b2cf")

# ── search strip ──────────────────────────────────────────────────────────────
st.markdown('<div class="search-strip">', unsafe_allow_html=True)
st.markdown('<div class="search-label">Choose a movie you enjoy</div>', unsafe_allow_html=True)

col_sel, col_btn = st.columns([4, 1], gap="medium")
with col_sel:
    selected_movie = st.selectbox(
        label="movie_select",
        options=movies,
        label_visibility="collapsed",
        placeholder="Search or select a movie…",
    )
with col_btn:
    recommend_clicked = st.button("🎬 Recommend", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── results ───────────────────────────────────────────────────────────────────
if recommend_clicked:
    if not selected_movie:
        st.warning("Please select a movie first.")
    else:
        with st.spinner(f"Finding movies similar to *{selected_movie}*…"):
            recommendations = recommend(selected_movie, model_data)

            # Pre-fetch details + images
            all_details = []
            all_images  = []
            for title in recommendations:
                d   = get_movie_details(title, OMDB_API_KEY)
                img = fetch_poster(d["poster"])
                all_details.append(d)
                all_images.append(img)

        if not recommendations:
            st.error(
                "Could not generate recommendations. "
                "Verify your model dict contains 'movies' and 'similarity' keys."
            )
        else:
            st.markdown('<div style="height:1px;background:#e2ddd8;margin:1.8rem 0;"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="font-family:Fraunces, serif; font-size:1.55rem; font-weight:700; color:#1a1a2e; margin-bottom:1.6rem;">Because you liked <em style="color:#e05c2a;">{selected_movie}</em></div>',
                unsafe_allow_html=True,
            )

            cols = st.columns(5, gap="medium")

            for idx, col in enumerate(cols):
                movie_name = recommendations[idx]
                details    = all_details[idx]
                img        = all_images[idx]

                rating_badge = (
                    f'<span style="background:#fff8f5; border:1px solid #f5cbb7; color:#c0440a; font-size:0.68rem; font-weight:600; padding:0.18em 0.65em; border-radius:999px;">⭐ {details["rating"]}</span>'
                    if details["rating"] not in (None, "N/A", "")
                    else ""
                )
                year_badge = (
                    f'<span style="color:#b5a898; font-size:0.72rem;">{details["year"]}</span>'
                    if details["year"] not in (None, "N/A", "")
                    else ""
                )
                plot_text = details["plot"] if details["plot"] not in (None, "N/A", "") else "No description available."

                with col:
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.markdown('<div class="poster-ph">🎬<small>No Poster</small></div>', unsafe_allow_html=True)

                    st.markdown(
                        f"""
                        <div class="card-rank-bar">
                            <span class="rank-dot"></span>
                            <span class="rank-text">#{idx + 1} pick</span>
                        </div>
                        <div class="card-body">
                            <div class="card-title">{movie_name}</div>
                            <div class="card-meta">{rating_badge}{year_badge}</div>
                            <div class="card-plot">{plot_text}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

# ── footer ────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">CineMatch &nbsp;·&nbsp; Built with Streamlit &amp; scikit-learn &nbsp;·&nbsp; Movie data via OMDb API</div>',
    unsafe_allow_html=True,
)