from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from google.cloud import firestore
from datetime import datetime
import os

app = FastAPI()

class DeleteRequest(BaseModel):
    uids: List[str]

# Load environment variables in development environment
if os.environ.get("ENV") == "development":
    from dotenv import load_dotenv
    load_dotenv()

# Get the current directory of the file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the credentials file
credentials_path = os.path.join(current_dir, 'CREDENTIALS.json')

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

# Initialize Firestore client
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

@app.delete("/delete_data/{uid}")
async def delete_data(uid: str):
    # Query Firestore to find the document with the given UID
    docs = db.collection('parking_sensors').where('uid', '==', uid).stream()

    deleted = False
    for doc in docs:
        # Delete the document
        doc.reference.delete()
        deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document with UID {uid} not found")
    
    return {"message": f"Document with UID {uid} deleted successfully"}
