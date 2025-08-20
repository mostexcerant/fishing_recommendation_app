# Fishing Recommendation System - Deployment Ready Scaffold

This repository provides a production-ready scaffold for:
- Backend: FastAPI app with endpoints for weather, travel, license, gear and a trip planner.
- Frontend: React app that calls the backend to plan trips.
- Mobile: Sample Expo/React Native app.
- Infra: docker-compose to run the backend.

## Setup (local dev)
1. Backend
   - cd backend
   - copy .env.example to .env and set keys (OPENWEATHER_KEY, GOOGLE_MAPS_KEY, OPENAI_API_KEY)
   - python -m venv .venv
   - pip install -r requirements.txt
   - uvicorn main:app --reload --port 8000

2. Frontend
   - cd frontend
   - npm install
   - npm start (configure proxy or CORS to backend)

3. Mobile (Expo)
   - Follow README in mobile/

## Notes
- The backend contains mock data and patterns for integrating real APIs and OpenAI.
- For agentic workflows, implement function-calling with OpenAI's API or use LangChain in the backend.
- Deploy backend to your cloud provider (AWS ECS, Heroku, GCP, etc.) and serve frontend from CDN.
