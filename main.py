from fastapi import FastAPI
from pydantic import BaseModel
import requests
from typing import List

app = FastAPI()

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
        if data.distance < 100:
            # Modify the message format here
            message = (
                f"\n🚗 Parking Alert for Lot '{data.uid}' 🚗\n"
                f"➤ Distance Detected: {data.distance} cm\n"
                f"➤ Status: A car is parked in Lot '{data.uid}'.\n"
                f"Stay safe and park responsibly!"
            )
            send_line_notify(message)
            print(f"Notification sent for {data.uid}")

    return {"message": "Batch data processed successfully"}


@app.get("/_ah/health")
def health_check():
    return {"status": "healthy"}