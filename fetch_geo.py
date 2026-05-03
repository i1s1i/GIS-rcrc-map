"""
Fetches Riyadh neighbourhoods/suburbs from Overpass API
and saves them as GeoJSON for use in the Dash map.
"""
import requests, json, os, math

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "RiyadhDashboard/1.0"}
OUTPUT_PATH = "data/riyadh_districts.geojson"

os.makedirs("data", exist_ok=True)

# ── Step 1: Get all suburb/neighbourhood relations in Riyadh bounding box ──
print("Fetching district list...")
list_query = """[out:json][timeout:60];
(
  relation['place'='suburb']['name'](24.5,46.5,25.1,47.0);
  relation['place'='neighbourhood']['name'](24.5,46.5,25.1,47.0);
);
out tags;"""

r = requests.post(OVERPASS_URL, data={"data": list_query}, headers=HEADERS, timeout=65)
districts_raw = r.json().get("elements", [])
print(f"  Found {len(districts_raw)} districts")

# ── Step 2: Fetch geometry for each (in batches to avoid timeout) ──
def classify_sector(lat, lon):
    """Classify district into N/S/E/W/Center based on coordinates."""
    clat, clon = 24.7136, 46.6753   # Riyadh center
    dlat = lat - clat
    dlon = lon - clon
    dist = math.sqrt(dlat**2 + dlon**2)
    if dist < 0.08:
        return "وسط"
    angle = math.degrees(math.atan2(dlon, dlat))
    if -45 <= angle < 45:
        return "شمال"
    elif 45 <= angle < 135:
        return "شرق"
    elif angle >= 135 or angle < -135:
        return "جنوب"
    else:
        return "غرب"

SECTOR_COLORS = {
    "شمال":  "#3B82F6",   # blue
    "شرق":   "#10B981",   # green
    "جنوب":  "#F59E0B",   # amber
    "غرب":   "#8B5CF6",   # purple
    "وسط":   "#EF4444",   # red
}

print("Fetching geometry for each district...")
features = []

ids = [e["id"] for e in districts_raw]
# Batch into groups of 50
batch_size = 50

for batch_start in range(0, len(ids), batch_size):
    batch = ids[batch_start:batch_start+batch_size]
    ids_str = "".join(f"relation({rid});" for rid in batch)
    geo_query = f"""[out:json][timeout:90];
({ids_str});
(._;>;);
out body;"""
    try:
        gr = requests.post(OVERPASS_URL, data={"data": geo_query}, headers=HEADERS, timeout=95)
        geo_data = gr.json().get("elements", [])
    except Exception as e:
        print(f"  Batch error: {e}")
        continue

    # Build node lookup
    nodes = {e["id"]: (e["lat"], e["lon"]) for e in geo_data if e["type"] == "node"}
    ways  = {e["id"]: e for e in geo_data if e["type"] == "way"}

    for rel in geo_data:
        if rel["type"] != "relation":
            continue
        tags = rel.get("tags", {})
        name_ar = tags.get("name:ar", tags.get("name", "غير معروف"))

        # Build polygon from outer members
        coords = []
        for member in rel.get("members", []):
            if member["type"] == "way" and member.get("role") in ("outer", ""):
                way = ways.get(member["ref"])
                if way:
                    ring = []
                    for nid in way.get("nodes", []):
                        nd = nodes.get(nid)
                        if nd:
                            ring.append([nd[1], nd[0]])   # [lon, lat] for GeoJSON
                    coords.extend(ring)

        if len(coords) < 4:
            continue

        # Centroid
        avg_lon = sum(c[0] for c in coords) / len(coords)
        avg_lat = sum(c[1] for c in coords) / len(coords)
        sector = classify_sector(avg_lat, avg_lon)

        feature = {
            "type": "Feature",
            "properties": {
                "id": rel["id"],
                "name_ar": name_ar,
                "name_en": tags.get("name:en", ""),
                "sector": sector,
                "color": SECTOR_COLORS[sector],
                "place": tags.get("place", ""),
                "centroid_lat": avg_lat,
                "centroid_lon": avg_lon,
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }
        features.append(feature)

    print(f"  Processed batch {batch_start//batch_size + 1}, total features so far: {len(features)}")

geojson = {"type": "FeatureCollection", "features": features}

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False)

print(f"\nDone! Saved {len(features)} district polygons to {OUTPUT_PATH}")
sector_counts = {}
for feat in features:
    s = feat["properties"]["sector"]
    sector_counts[s] = sector_counts.get(s, 0) + 1
print("Sector breakdown:", sector_counts)
