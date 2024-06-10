import asyncio
import websockets
import json

async def handle_connection(websocket, path):
    print("Client connected")
    await send_message(websocket, {"message": "Hello from the server!"})
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            try:
                data = json.loads(message)
                response = handle_message(data)
                await send_message(websocket, response)
                print(f"Sent response: {response}")
            except json.JSONDecodeError:
                print("Received non-JSON message")

    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")

def handle_message(data):
    if "message" in data:
        return {"type": "response", "message": "Received message"}
    else:
        return {"type": "error", "message": "Unknown message type"}

async def send_message(websocket, message):
    await websocket.send(json.dumps(message))

async def main():
    server = await websockets.serve(handle_connection, "localhost", 7272)
    print("Server started")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
