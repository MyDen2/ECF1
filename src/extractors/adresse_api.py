import time
import requests

def geocode_address(query: str, user_agent: str, delay_s: float = 0.2):
    """
    Retourne dict: {label, score, lon, lat} ou None si pas trouvé.
    delay_s: politesse
    """
    url = "https://api-adresse.data.gouv.fr/search/"
    headers = {"User-Agent": user_agent}

    params = {"q": query, "limit": 1}
    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()

    data = r.json()
    feats = data.get("features", [])
    if not feats:
        return None

    f = feats[0]
    coords = f["geometry"]["coordinates"]  # [lon, lat]
    props = f["properties"]

    time.sleep(delay_s)

    return {
        "label": props.get("label"),
        "score": props.get("score"),
        "lon": coords[0],
        "lat": coords[1],
    }
