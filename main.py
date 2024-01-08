from fastapi import FastAPI
from pydantic import BaseModel
import requests
from typing import List
from google.cloud import firestore
from datetime import datetime

app = FastAPI()
db = firestore.Client()

class SensorData(BaseModel):
    uid: str
    distance: int

line_notify_token = "FREfyO6xOlbbIh4qzFWoiFiZJX1Y7RJIxBTBAXiDn51"
line_notify_api = "https://notify-api.line.me/api/notify"

def send_line_notify(message: str):
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': message}
    response = requests.post(line_notify_api, headers=headers, data=data)
    return response.status_code


@app.post("/receive_data")
async def receive_data(sensor_data: List[SensorData]):
    for data in sensor_data:
        status = "Occupied" if data.distance < 100 else "Free"  # adjust as per your logic
        # Add data to Firestore
        doc_ref = db.collection('parking_sensors').document()
        doc_ref.set({
            'uid': data.uid,
            'distance': data.distance,
            'timestamp': datetime.utcnow(),  # Firestore converts this to its Timestamp type
            'status': status
        })
        # Your existing logic for notifications, etc.
    return {"message": "Data processed and stored in Firestore"}

# @app.post("/receive_data")
# async def receive_data(sensor_data: List[SensorData]):
#     for data in sensor_data:
#         if data.distance < 100:
#             # Modify the message format here
#             message = (
#                 f"\n🚗 Parking Alert for Lot '{data.uid}' 🚗\n"
#                 f"➤ Distance Detected: {data.distance} cm\n"
#                 f"➤ Status: A car is parked in Lot '{data.uid}'.\n"
#                 f"Stay safe and park responsibly!"
#             )
#             send_line_notify(message)
#             print(f"Notification sent for {data.uid}")

#     return {"message": "Batch data processed successfully"}


@app.get("/_ah/health")
def health_check():
    return {"status": "healthy"}