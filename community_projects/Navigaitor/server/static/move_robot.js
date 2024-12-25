// Establish WebSocket connection to the FastAPI WebSocket endpoint
const socket = new WebSocket("ws://localhost:8000/move");

// Handle WebSocket messages from the server
socket.onmessage = function(event) {
  const keyDisplay = document.getElementById("keyPressDisplay");
  keyDisplay.innerHTML = `Server response: <strong>${event.data}</strong>`;
};

// Handle WebSocket errors
socket.onerror = function(error) {
  console.error("WebSocket Error:", error);
};
	
	document.addEventListener('keydown', (e) => {
		if (e.repeat) return;
		socket.send(`{"pressed" : "${event.key}"}`);
	});

	document.addEventListener('keyup', (e) => {
                if (e.repeat) return;
                socket.send(`{"released" : "${event.key}"}`);
        });
