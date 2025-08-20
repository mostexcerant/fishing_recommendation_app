import React, { useState } from "react";
import axios from "axios";
import "./styles.css";

export default function App() {
  const [species, setSpecies] = useState("");
  const [state, setState] = useState("");
  const [userLocation, setUserLocation] = useState("");
  const [destination, setDestination] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const planTrip = async () => {
    setLoading(true);
    try {
      const res = await axios.post("/api/plan_trip", {
        species,
        state,
        user_location: userLocation,
        destination_name: destination
      });
      setResponse(res.data);
    } catch (e) {
      setResponse({ error: e.message });
    }
    setLoading(false);
  };

  return (
    <div className="app">
      <h1>Fishing Trip Planner</h1>
      <div className="form">
        <input placeholder="Species (e.g., bass)" value={species} onChange={e=>setSpecies(e.target.value)} />
        <input placeholder="State (e.g., Maine)" value={state} onChange={e=>setState(e.target.value)} />
        <input placeholder="Your city or ZIP" value={userLocation} onChange={e=>setUserLocation(e.target.value)} />
        <input placeholder="Destination (lake or town)" value={destination} onChange={e=>setDestination(e.target.value)} />
        <button onClick={planTrip} disabled={loading}>Plan Trip</button>
      </div>
      <div className="result">
        {loading && <p>Planning...</p>}
        {response && <pre>{JSON.stringify(response, null, 2)}</pre>}
      </div>
    </div>
  );
}
