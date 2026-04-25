import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
import json
from src.utils import load_metadata

load_dotenv()
CLIENT_ID = os.getenv('SH_ID') 
CLIENT_SECRET = os.getenv('SH_SECRET') 

def get_token():
    auth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    r = requests.post(auth_url, data={"grant_type": "client_credentials", "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET})
    r.raise_for_status()
    return r.json().get("access_token")

def generate_grid(bbox, krok):
    min_lon, min_lat, max_lon, max_lat = bbox
    sectors = []
    idx = 1
    curr_lon = min_lon
    while curr_lon < max_lon:
        curr_lat = min_lat
        while curr_lat < max_lat:
            sectors.append({
                "ID": f"S_{idx}",
                "bbox": [curr_lon, curr_lat, curr_lon + krok, curr_lat + krok],
                "lat": round(curr_lat + (krok/2), 5),
                "lon": round(curr_lon + (krok/2), 5)
            })
            idx += 1
            curr_lat += krok
        curr_lon += krok
    return sectors

def round_fr(wartosc, miejsca_po_przecinku=4):
    try:
        return round(float(wartosc), miejsca_po_przecinku)
    except (ValueError, TypeError):
        return None
    

    
def get_data(REGION_NAME):

    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = "https://sh.dataspace.copernicus.eu/api/v1/statistics"


    try:
        meta = load_metadata(REGION_NAME)
        BBOX = meta['bbox']
        SECTOR_SIZE = meta['sector_size']
        print(f"Metadata loaded for {REGION_NAME}: bbox={BBOX}")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    sectors = generate_grid(BBOX, SECTOR_SIZE)
    
    evalscript = """
    //VERSION=3
    function setup() {
      return {
        input: ["B03", "B04", "B08", "B11", "SCL", "dataMask"],
        output: [
          { id: "ndvi", bands: 1 },
          { id: "ndwi", bands: 1 },
          { id: "ndmi", bands: 1 },
          { id: "dataMask", bands: 1 }
        ]
      };
    }
    function evaluatePixel(samples) {

        if ([3, 8, 9, 10].includes(samples.SCL) || samples.dataMask === 0) {
          return { ndvi: [NaN], ndwi: [NaN], ndmi: [NaN], dataMask: [0] };
      }
      let ndvi = (samples.B08 - samples.B04) / (samples.B08 + samples.B04);
      let ndwi = (samples.B03 - samples.B08) / (samples.B03 + samples.B08);
      let ndmi = (samples.B08 - samples.B11) / (samples.B08 + samples.B11);
      
      return { ndvi: [ndvi], ndwi: [ndwi], ndmi: [ndmi], dataMask: [1] };
    }
    """
    all_data = []

    for i, s in enumerate(sectors):
        print(f"{i+1}/{len(sectors)}: {s['ID']} ({REGION_NAME})", end="\r")
        payload = {
            "input": {
                "bounds": {"bbox": s['bbox']},
                "data": [{"type": "sentinel-2-l2a", "dataFilter": {"mosaickingOrder": "leastCC"}}]
            },
            "aggregation": {
                "timeRange": {"from": "2025-06-01T00:00:00Z", "to": "2026-04-20T00:00:00Z"},
                "aggregationInterval": {"of": "P1M"},
                "evalscript": evalscript,
                "resx": 0.0005, "resy": 0.0005
            }
        }

        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json()
            for item in data['data']:
                data_iso = item['interval']['from'][:10]
                
                out = item['outputs']
                if out['ndvi']['bands']['B0']['stats']['sampleCount'] > 0:
                    all_data.append({
                        "Sektor_ID": s['ID'],
                        "Lat": s['lat'],
                        "Lon": s['lon'],
                        "Data": data_iso,
                        "NDVI": round_fr(out['ndvi']['bands']['B0']['stats']['mean'], 4),
                        "NDWI": round_fr(out['ndwi']['bands']['B0']['stats']['mean'], 4),
                        "NDMI": round_fr(out['ndmi']['bands']['B0']['stats']['mean'], 4)
                    })
        time.sleep(0.4)

    df = pd.DataFrame(all_data)

    DATA_FOLDER = os.path.join("..", "data")
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    OUTPUT_FILE = os.path.join(DATA_FOLDER, REGION_NAME, "raw.csv")

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✨ Results saved in {OUTPUT_FILE}")



