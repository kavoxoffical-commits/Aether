"""Select random beautiful location"""
import json
import random
from pathlib import Path
from datetime import datetime

LOCATIONS = [
    {"name": "Victoria Falls", "country": "Zimbabwe", "queries": ["waterfall", "victoria falls", "scenic waterfall"]},
    {"name": "Northern Lights", "country": "Iceland", "queries": ["aurora", "northern lights", "aurora borealis"]},
    {"name": "Mount Everest", "country": "Nepal", "queries": ["mountain", "everest", "snow peak"]},
    {"name": "Great Barrier Reef", "country": "Australia", "queries": ["coral reef", "ocean", "underwater"]},
    {"name": "Sahara Desert", "country": "Morocco", "queries": ["desert", "sand dunes", "sahara"]},
    {"name": "Banff Lake", "country": "Canada", "queries": ["lake", "mountains", "forest"]},
    {"name": "Patagonia", "country": "Argentina", "queries": ["glacier", "mountains", "landscape"]},
    {"name": "Bali Temple", "country": "Indonesia", "queries": ["temple", "tropical", "nature"]},
    {"name": "Swiss Alps", "country": "Switzerland", "queries": ["alpine", "mountains", "peaks"]},
    {"name": "Amazon Rainforest", "country": "Brazil", "queries": ["jungle", "forest", "wildlife"]},
]

def select_location():
    location = random.choice(LOCATIONS)
    
    tracking_file = Path("/tmp/places_v2/data/tracking.json")
    
    if tracking_file.exists():
        records = json.loads(tracking_file.read_text())
    else:
        records = []
    
    place_id = f"place_{len(records) + 1:04d}"
    record = {
        "id": place_id,
        "name": location["name"],
        "country": location["country"],
        "search_queries": location["queries"],
        "videos": [],
        "status": "selected",
        "created_at": datetime.now().isoformat()
    }
    
    records.append(record)
    tracking_file.write_text(json.dumps(records, indent=2))
    
    print(f"✅ Selected: {location['name']}, {location['country']}")
    return record

if __name__ == "__main__":
    select_location()
