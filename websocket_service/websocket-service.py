import asyncio
import redis.asyncio as redis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# This will hold all active WebSocket connections
connections: list[WebSocket] = []

# Redis configuration
redis_host = 'localhost'
redis_port = 6379
redis_channel = 'update'

# Initialize Redis client
redis_client = redis.Redis(host=redis_host, port=redis_port)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            # Just to keep the connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.remove(websocket)


async def redis_listener():
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(redis_channel)
    async for message in pubsub.listen():
        # Skip over the initial subscribing message
        if message['type'] == 'message':
            msg_data = message['data']
            if msg_data:
                await broadcast_message(msg_data.decode('utf-8'))


async def broadcast_message(message: str):
    print(f"Broadcasting message: {message}")  # Added print statement
    for connection in connections:
        await connection.send_text(message)

@app.on_event("startup")
async def startup_event():
    # Run the Redis listener in the background
    asyncio.create_task(redis_listener())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="10.10.10.1", port=3001)
