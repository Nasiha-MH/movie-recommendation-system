"""
src/utils.py
────────────
OMDb API integration.
Fetches movie poster, IMDb rating, plot, and release year.
"""

import requests

# CORRECT
OMDB_BASE_URL = "http://www.omdbapi.com/"
# Cache results in memory to avoid redundant API calls during a session
_cache: dict[str, dict] = {}


def get_movie_details(movie_name: str, api_key: str) -> dict:
    """
    Fetch movie details from the OMDb API.

    Parameters
    ----------
    movie_name : str
        Title of the movie to look up.
    api_key : str
        Your personal OMDb API key (free at https://www.omdbapi.com/apikey.aspx).

    Returns
    -------
    dict with keys:
        poster  : str  — URL to the movie poster image (or "N/A")
        rating  : str  — IMDb rating, e.g. "8.3" (or "N/A")
        plot    : str  — Short plot description (or "N/A")
        year    : str  — Release year, e.g. "1994" (or "N/A")
        title   : str  — Official movie title from OMDb (or original name)
    """
    cache_key = movie_name.lower().strip()

    # Return cached result if available
    if cache_key in _cache:
        return _cache[cache_key]

    # Default fallback response
    fallback = {
        "poster": "N/A",
        "rating": "N/A",
        "plot":   "N/A",
        "year":   "N/A",
        "title":  movie_name,
    }

    # Guard against placeholder / missing key
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return fallback

    try:
        params = {
            "t":      movie_name,
            "apikey": api_key,
            "plot":   "short",
            "r":      "json",
        }
        response = requests.get(OMDB_BASE_URL, params=params, timeout=8)
        response.raise_for_status()

        data = response.json()

        if data.get("Response") == "True":
            result = {
                "poster": data.get("Poster", "N/A"),
                "rating": data.get("imdbRating", "N/A"),
                "plot":   data.get("Plot", "N/A"),
                "year":   data.get("Year", "N/A"),
                "title":  data.get("Title", movie_name),
            }
        else:
            # OMDb returned an error (movie not found, wrong title, etc.)
            print(f"[WARN] OMDb: {data.get('Error', 'Unknown error')} for '{movie_name}'")
            result = fallback

    except requests.exceptions.ConnectionError:
        print("[WARN] No internet connection. Returning fallback details.")
        result = fallback
    except requests.exceptions.Timeout:
        print(f"[WARN] OMDb request timed out for '{movie_name}'.")
        result = fallback
    except Exception as e:
        print(f"[ERROR] Unexpected error fetching details for '{movie_name}': {e}")
        result = fallback

    # Store in session cache
    _cache[cache_key] = result
    return result


def clear_cache() -> None:
    """Clear the in-memory API response cache."""
    _cache.clear()
