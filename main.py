from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from google.cloud import firestore
from datetime import datetime
import os
import pytz


app = FastAPI()

class SensorData(BaseModel):
    uid: str
    distance: int

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

from datetime import datetime

@app.get("/")
def read_root():
    # Get the UTC+7 timezone
    utc_plus_7 = pytz.timezone('Asia/Bangkok')
    current_utc_time = datetime.now(utc_plus_7)

    # Show the collection name based on the current date in UTC+7
    collection_name = f"parking_sensors_{current_utc_time.strftime('%Y%m%d')}"
    
    changelog = {
        "Version 3.2": [
            "# Dynamic creation of Firestore collections based on the current date.",
            "# Each collection is named 'parking_sensors_YYYYMMDD' to store daily sensor data.",
            "# Deletion endpoint updated to specify the date or range of dates for deletion.",
            "# Fix Time Zone to UTC+7.",
            "# Add error handling."
        ]
    }
    return {"message": "Welcome to my FastAPI application!", "changelog": changelog, "current_utc_time": current_utc_time, "Firestore collection_name": collection_name}


@app.post("/receive_data")
async def receive_data(sensor_data: List[SensorData]):
    # Get the UTC+7 timezone
    utc_plus_7 = pytz.timezone('Asia/Bangkok')
    
    # Convert the current time to UTC+7
    current_time = datetime.now(utc_plus_7)
    
    # Generate a collection name based on the current date in UTC+7
    collection_name = f"parking_sensors_{current_time.strftime('%Y%m%d')}"

    for data in sensor_data:
        status = "Occupied" if data.distance < 200 else "Free"
        # Convert the timestamp to UTC+7 and add data to Firestore in the date-specific collection
        timestamp_utc_plus_7 = current_time.astimezone(pytz.utc)
        doc_ref = db.collection(collection_name).document()
        doc_ref.set({
            'uid': data.uid,
            'distance': data.distance,
            'timestamp': timestamp_utc_plus_7,
            'status': status
        })

    return {"message": "Data processed and stored in Firestore"}



@app.get("/_ah/health")
def health_check():
    return {"status": "healthy"}

@app.delete("/delete_data/{date_for_deletion}/{uid}")
async def delete_data(date_for_deletion: str, uid: str):
    # Check if the provided date_for_deletion is in the correct format (YYYYMMDD)
    if not date_for_deletion.isdigit() or len(date_for_deletion) != 8:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYYMMDD.")

    collection_name = f"parking_sensors_{date_for_deletion}"

    # Query Firestore to find the document with the given UID
    docs = db.collection(collection_name).where('uid', '==', uid).stream()

    deleted = False
    for doc in docs:
        # Delete the document
        doc.reference.delete()
        deleted = True

    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document with UID {uid} not found")
    
    return {"message": f"Document with UID {uid} deleted successfully from collection {collection_name}"}
