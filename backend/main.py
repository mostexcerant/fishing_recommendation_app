"""
FastAPI backend for Fishing Recommendation App
- Provides endpoints for weather, travel, license, gear
- Shows example integration points for OpenAI function calling / agent
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests

app = FastAPI(title="Fishing Recommendation Backend")

# Load env vars (expected to be set in deployment)
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY", "")
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ---------- Schemas ----------
class GearRequest(BaseModel):
    species: str
    water_type: str
    experience_level: str
    user_location: Optional[str] = None

class TravelRequest(BaseModel):
    origin: str
    destination: str

class LicenseRequest(BaseModel):
    state: str
    residency: str

# ---------- Mock / Helper functions ----------
def fetch_weather(lat: float, lon: float):
    if not OPENWEATHER_KEY:
        return {"warning": "OPENWEATHER_KEY not set", "mock": True}
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={OPENWEATHER_KEY}&units=imperial"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def google_distance_matrix(origin: str, destination: str):
    if not GOOGLE_MAPS_KEY:
        return {"warning": "GOOGLE_MAPS_KEY not set", "mock_distance": "120 miles", "mock_duration": "2 hours"}
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {"origins": origin, "destinations": destination, "key": GOOGLE_MAPS_KEY, "mode": "driving"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    elem = data["rows"][0]["elements"][0]
    return {"distance": elem.get("distance", {}).get("text"), "duration": elem.get("duration", {}).get("text")}

# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/weather")
def weather(lat: float, lon: float):
    try:
        return fetch_weather(lat, lon)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/travel")
def travel(req: TravelRequest):
    try:
        return google_distance_matrix(req.origin, req.destination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/license")
def license_info(req: LicenseRequest):
    # In production, replace with DB / authoritative sources for each state.
    sample = {
        "Maine": {"resident":"$25","nonresident":"$64","url":"https://www.maine.gov/ifw/licenses-permits/fishing/index.html"},
        "Florida": {"resident":"$17","nonresident":"$47","url":"https://myfwc.com/"},
        "Texas": {"resident":"$30","nonresident":"$58","url":"https://tpwd.texas.gov/"}
    }
    return sample.get(req.state, {"error": "state not in sample DB"})

@app.post("/gear")
def gear(req: GearRequest):
    # Replace this with real product DB + scoring & prioritization logic
    catalog = [
        {"id":"rod001","name":"Falcon Strike 7'2 MH","type":"rod","best_for":["bass","pike"],"conditions":["freshwater"],"priority":1,"price":199.0,"url":"https://example.com/products/rod001"},
        {"id":"rod002","name":"Falcon Surf 10' Medium","type":"rod","best_for":["striped bass"],"conditions":["saltwater","surf"],"priority":1,"price":229.0,"url":"https://example.com/products/rod002"},
        {"id":"reel001","name":"Stealth 3000","type":"reel","best_for":["bass","striped bass"],"conditions":["freshwater","saltwater"],"priority":1,"price":129.0,"url":"https://example.com/products/reel001"}
    ]
    # Simple filter scoring
    matches = []
    for p in catalog:
        score = 0
        if req.species.lower() in ",".join(p["best_for"]).lower():
            score += 10
        if req.water_type.lower() in ",".join(p["conditions"]).lower():
            score += 5
        score += (10 - p["priority"])  # lower priority number -> boost
        matches.append((score, p))
    matches.sort(reverse=True, key=lambda x: x[0])
    recommended = [m[1] for m in matches][:5]
    return {"recommended": recommended, "count": len(recommended)}

# Endpoint demonstrating a combined trip plan (calls other internal endpoints)
class TripRequest(BaseModel):
    species: str
    state: str
    month: Optional[str] = None
    user_location: Optional[str] = None
    residency: Optional[str] = "resident"
    experience_level: Optional[str] = "intermediate"
    water_type: Optional[str] = "freshwater"
    destination_name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

@app.post("/plan_trip")
def plan_trip(req: TripRequest):
    # 1) Check season (mock)
    seasons = {
        ("Maine","striped bass"): {"open":"May 15","close":"Oct 1","in_season": True},
        ("Florida","snook"): {"open":"Mar 1","close":"Apr 30","in_season": True}
    }
    season = seasons.get((req.state, req.species.lower()), {"in_season": False})
    # 2) Get gear
    gear_resp = gear(GearRequest(species=req.species, water_type=req.water_type, experience_level=req.experience_level, user_location=req.user_location))
    # 3) License
    license_resp = license_info(LicenseRequest(state=req.state, residency=req.residency))
    # 4) Travel (mock/dummy if no user_location)
    travel_resp = {"distance":"unknown","duration":"unknown"}
    if req.user_location and req.destination_name:
        try:
            travel_resp = google_distance_matrix(req.user_location, req.destination_name)
        except Exception:
            travel_resp = {"warning":"google api failed or key not set", "mock_distance":"120 miles", "mock_duration":"2 hours"}
    # 5) Weather (if lat/lon)
    weather_resp = None
    if req.lat and req.lon:
        try:
            weather_resp = fetch_weather(req.lat, req.lon)
        except Exception:
            weather_resp = {"warning":"weather failed or key not set"}
    return {
        "species": req.species,
        "state": req.state,
        "season": season,
        "gear": gear_resp,
        "license": license_resp,
        "travel": travel_resp,
        "weather": weather_resp
    }
