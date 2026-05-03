import requests
import json
import os

BASE_URL = "https://data.rcrc.gov.sa/api/explore/v2.1/catalog/datasets"

DATASETS = {
    "metro_stations": "metro-stations-in-riyadh-by-metro-line-and-station-type-2024", "metro_lines": "metro-lines-in-riyadh-2024", "bus_routes": "bus-roads-by-direction-in-riyadh-2024",
    "bus_stops": "bus-stops-in-riyadh-by-bus-route-direction-and-shelter-type-2024",
    "entertainment": "entertainment-services-by-sub-municipality-and-district-2024",
    "air_quality": "air-quality-stations-in-riyadh-2025"
}

def fetch_and_save(name, dataset_id):
    url = f"{BASE_URL}/{dataset_id}/records?limit=100"
    print(f"Fetching {name} from {url}...")
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
        response.raise_for_status()
        data = response.json()
        
        os.makedirs('data', exist_ok=True)
        with open(f'data/{name}.json', 'w', encoding='utf-8') as f:
            json.dump(data.get('results', []), f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data.get('results', []))} records to data/{name}.json")
    except Exception as e:
        print(f"Error fetching {name}: {e}")

if __name__ == "__main__":
    for name, dataset_id in DATASETS.items():
        fetch_and_save(name, dataset_id)
