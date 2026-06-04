import numpy as np
import faiss
from src.utils.database import get_all_city_vectors

FEATURES = ["pulse_score", "weather_score", "air_score", "temperature", "aqi"]

def get_similar_cities(city_name: str, top_n: int = 3) -> list | None:
    rows = get_all_city_vectors()
    if len(rows) < 2:
        return None

    # filter out rows with missing features
    rows = [r for r in rows if all(r.get(f) is not None for f in FEATURES)]
    if len(rows) < 2:
        return None

    names = [r["city_name"] for r in rows]
    if city_name not in names:
        return None

    matrix = np.array(
        [[r[f] for f in FEATURES] for r in rows],
        dtype=np.float32
    )

    # normalise each feature to [0, 1]
    mins = matrix.min(axis=0)
    maxs = matrix.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1  # avoid divide by zero
    matrix = (matrix - mins) / ranges

    index = faiss.IndexFlatL2(len(FEATURES))
    index.add(matrix)

    query_idx = names.index(city_name)
    query = matrix[query_idx:query_idx + 1]

    # fetch top_n + 1 to exclude the city itself
    distances, indices = index.search(query, top_n + 1)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        name = names[idx]
        if name == city_name:
            continue
        row = rows[idx]
        results.append({
            "city": name,
            "similarity_score": round(float(1 / (1 + dist)), 3),
            "pulse_score": row["pulse_score"],
            "temperature": row["temperature"],
            "aqi": row["aqi"]
        })
        if len(results) == top_n:
            break

    return results