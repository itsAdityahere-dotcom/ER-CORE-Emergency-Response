from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

app = FastAPI(title="ER-CORE API", version="1.0.0")

class IncidentCreate(BaseModel):
    type: str
    severity: str
    location: str
    description: str = ""
    people_affected: int = 1

incidents = []

@app.get("/api/v1/health")
def health():
    return {"status":"operational","mode":"simulation","time":datetime.utcnow().isoformat()}

@app.get("/api/v1/incidents")
def list_incidents():
    return incidents

@app.post("/api/v1/incidents")
def create_incident(item: IncidentCreate):
    obj = {"id": f"INC-{1000+len(incidents)+1}", **item.model_dump(),
           "status":"REPORTED","created_at":datetime.utcnow().isoformat()}
    incidents.append(obj)
    return obj

@app.post("/api/v1/ml/severity/predict")
def severity_predict(item: IncidentCreate):
    base = {"LOW":.03,"MEDIUM":.07,"HIGH":.18,"CRITICAL":.72}
    return {"prediction":item.severity,"probabilities":base,"model":"RandomForest-demo","version":"1.0"}

@app.get("/api/v1/dispatch/recommendations/{incident_id}")
def recommendations(incident_id: str):
    return {"incident_id":incident_id,"recommendations":[
        {"ambulance_id":"AMB-102","score":93,"predicted_eta":7.1,"traffic":"LOW",
         "reason":["Lowest predicted ETA","Required equipment available","Ambulance available"]},
        {"ambulance_id":"AMB-001","score":78,"predicted_eta":9.4,"traffic":"MEDIUM",
         "reason":["Available","Close distance"]}
    ]}

@app.websocket("/ws/dashboard")
async def dashboard_socket(ws: WebSocket):
    await ws.accept()
    while True:
        await ws.send_json({"event":"SYSTEM_HEARTBEAT","timestamp":datetime.utcnow().isoformat()})
        await __import__("asyncio").sleep(5)
