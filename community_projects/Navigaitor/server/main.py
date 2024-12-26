from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from starlette.requests import Request
import logging
import uvicorn
import json
from server.move import move
from hailo_demo import MatchingDemo

# Initialize the FastAPI app
app = FastAPI()
matching_demo_obj = MatchingDemo()

# Set up logging (optional, for debugging)
logging.basicConfig(level=logging.INFO)

@app.post("/call_function_start_record")
async def call_function_start_record():
    print("call_function_start_record: Button was pressed!")
    matching_demo_obj.start_recording()

@app.post("/call_function_stop_record")
async def call_function_stop_record():
    print("call_function_stop_record: Button was pressed!")
    matching_demo_obj.stop_recording()

@app.post("/call_function_repeat_course")
async def call_function_repeat_course():
    print("call_function_repeat_course: Button was pressed!")
    # add parameter
    matching_demo_obj.start_playback()

@app.post("/call_function_retract_home")
async def call_function_retract_home():
    print("call_function_retract_home: Button was pressed!")
    # add parameter
    matching_demo_obj.start_playback()


# expecting: json in the format of `{"pressed" or "released": "forward" or "backward" or "left" or "right"}`
@app.websocket("/move")
async def move_robot(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        logging.info(f"Received message: {data}")
        move(json.loads(data))

# Endpoint to serve the HTML page with WebSocket client-side JavaScript
@app.get("/", response_class=FileResponse)
async def get_keypress_page(request: Request):
    # Render the HTML with embedded JavaScript for key events
    return FileResponse('./templates/keypress.html') 

def start():
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)

