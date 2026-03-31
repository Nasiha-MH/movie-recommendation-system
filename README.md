# 🎬 CineMatch — Movie Recommendation System

A machine-learning-powered movie recommendation web app built with **Streamlit** and **scikit-learn**, with rich movie details fetched live from the **OMDb API**.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🎯 Smart Recommendations | Top-5 similar movies from your trained cosine-similarity model |
| 🖼️ Movie Posters | Live poster images pulled from OMDb |
| ⭐ IMDb Ratings | Real-time ratings for every recommendation |
| 📖 Plot Summaries | Short descriptions to help you decide |
| 🔍 Searchable Dropdown | Instantly filter from thousands of titles |
| ⚡ Session Caching | API responses cached to avoid redundant calls |

---

## 🛠️ Technologies Used

- **Python 3.10+**
- **Streamlit** — interactive web frontend
- **scikit-learn** — cosine-similarity recommendation engine
- **pandas / numpy** — data handling
- **pickle / joblib** — model serialisation
- **requests** — HTTP calls to OMDb API
- **OMDb API** — movie metadata (poster, rating, plot)

---

## 📁 Project Structure

```
movie_recommendation_system/
│
├── app.py                  ← Streamlit frontend (run this)
│
├── src/
│   ├── __init__.py
│   ├── recommend.py        ← Model loading + recommendation logic
│   └── utils.py            ← OMDb API integration
│
├── model/
│   └── recommender.pkl     ← ⚠️  Export from Colab and place here
│
├── data/
│   └── movies.csv          ← Movie dataset (title, genres, overview …)
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 How to Run the Project in VS Code

### Step 1 — Clone / download the project

```bash
git clone https://github.com/your-username/movie-recommendation-system.git
cd movie_recommendation_system
```

### Step 2 — Create and activate a virtual environment *(recommended)*

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Add your OMDb API key

Open `app.py` and replace the placeholder on this line:

```python
OMDB_API_KEY = os.getenv("OMDB_API_KEY", "YOUR_API_KEY_HERE")
```

**Better practice** — set it as an environment variable so you never accidentally commit it:

```bash
# Windows (PowerShell)
$env:OMDB_API_KEY = "your_actual_key"

# macOS / Linux
export OMDB_API_KEY="your_actual_key"
```

### Step 5 — Place your trained model

Copy `recommender.pkl` (exported from Google Colab) into the `model/` folder.

### Step 6 — Launch the app

```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**

---

## 🧪 Export Your Model from Google Colab

### Save the model

At the end of your Colab training notebook, run:

```python
import pickle

# Bundle everything the app needs into one dictionary
model_data = {
    "movies":     movies,      # pd.DataFrame with a 'title' column  OR  list of movie titles
    "similarity": similarity   # cosine-similarity matrix — np.ndarray, shape (n, n)
}

with open("recommender.pkl", "wb") as f:
    pickle.dump(model_data, f)

print("✅ Model saved as recommender.pkl")
```

> **Tip:** If your similarity matrix is very large (> 100 MB), use `joblib` instead — it's faster for numpy arrays:
> ```python
> import joblib
> joblib.dump(model_data, "recommender.pkl")
> ```

### Download from Colab

```python
from google.colab import files
files.download("recommender.pkl")
```

### Place in the project

Move the downloaded file to:

```
movie_recommendation_system/
└── model/
    └── recommender.pkl   ← here
```

---

## 🔑 How to Get a Free OMDb API Key

1. Go to **https://www.omdbapi.com/apikey.aspx**
2. Choose the **Free** tier (1,000 requests/day)
3. Enter your email address and submit
4. Check your inbox and **activate** the key via the confirmation link
5. Copy the key and add it to `app.py` or set it as an environment variable

---

## 🧩 How the Recommendation Engine Works

```
User selects a movie
        │
        ▼
recommend(movie_name, model_data)
        │
        ├─ Finds the movie's index in the titles list
        ├─ Looks up its row in the cosine-similarity matrix
        ├─ Sorts all other movies by similarity score (descending)
        └─ Returns the top-5 most similar titles
                │
                ▼
        get_movie_details(title, api_key)   ← called for each recommendation
                │
                └─ Fetches poster · rating · plot · year from OMDb
```

The similarity matrix is pre-computed during training (typically via TF-IDF on genres/overviews + cosine similarity), so recommendations are **instant** at runtime.

---

## ⚠️ Troubleshooting

| Problem | Solution |
|---|---|
| `Model file not found` | Export `recommender.pkl` from Colab and place it in `model/` |
| Posters not loading | Check your OMDb API key is correct and activated |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside your virtual env |
| Blank recommendations | Ensure your model dict has `"movies"` and `"similarity"` keys |
| Port already in use | Run `streamlit run app.py --server.port 8502` |

---

## 📝 License

MIT — feel free to use, modify, and distribute.
