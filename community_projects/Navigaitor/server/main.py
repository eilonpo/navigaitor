from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request
import logging
import uvicorn
import json
from pathlib import Path
# from server.move import move

# Initialize the FastAPI app
app = FastAPI()

hls_path = Path(__file__).resolve().parent / "hls"
static_path = Path(__file__).resolve().parent / "static"

app.mount("/hls", StaticFiles(directory=hls_path), name="hls")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Set up logging (optional, for debugging)
logging.basicConfig(level=logging.INFO)

# expecting: json in the format of `{"pressed" or "released": "forward" or "backward" or "left" or "right"}`
@app.websocket("/move")
async def move_robot(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        logging.info(f"Received message: {data}")
        # move(json.loads(data))

# Endpoint to serve the HTML page with WebSocket client-side JavaScript
@app.get("/", response_class=FileResponse)
async def main(request: Request):
    # Render the HTML with embedded JavaScript for key events
    return FileResponse('./static/index.html') 

def start():
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)

