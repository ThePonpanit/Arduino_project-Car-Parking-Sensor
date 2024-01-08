from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from google.cloud import firestore
from datetime import datetime

app = FastAPI()
db = firestore.Client()

class SensorData(BaseModel):
    uid: str
    distance: int

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI application!"}

@app.post("/receive_data")
async def receive_data(sensor_data: List[SensorData]):
    for data in sensor_data:
        status = "Occupied" if data.distance < 100 else "Free"
        # Add data to Firestore
        doc_ref = db.collection('parking_sensors').document()
        doc_ref.set({
            'uid': data.uid,
            'distance': data.distance,
            'timestamp': datetime.utcnow(),
            'status': status
        })

    return {"message": "Data processed and stored in Firestore"}


@app.get("/_ah/health")
def health_check():
    return {"status": "healthy"}