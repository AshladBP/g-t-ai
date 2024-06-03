extends Node

var socket = WebSocketPeer.new()

func _ready():
    connect_to_server("wss://localhost:8080")

func _process(_delta):
    socket.poll()
    handle_socket_state()

func connect_to_server(url: String):
    var error = socket.connect_to_url(url)
    if error != OK:
        print("Failed to connect to WebSocket server: ", error)
    else:
        print("Connecting to WebSocket server...")

func handle_socket_state():
    var state = socket.get_ready_state()
    match state:
        WebSocketPeer.STATE_OPEN:
            process_packets()
        WebSocketPeer.STATE_CLOSING:
            # Continue polling until fully closed
            pass
        WebSocketPeer.STATE_CLOSED:
            notify_closure()
            set_process(false)

func process_packets():
    while socket.get_available_packet_count() > 0:
        var packet = socket.get_packet()
        print("Received packet: ", packet)

func notify_closure():
    var code = socket.get_close_code()
    var reason = socket.get_close_reason()
    print("WebSocket closed with code: %d, reason: %s. Clean: %s" % [code, reason, code != -1])

func send_json(data: Dictionary):
    var json_string = JSON.parse_string(JSON.stringify(data))
    var error = socket.send_text(json_string)
    if error != OK:
        print("Failed to send JSON data: ", error)
    else:
        print("JSON data sent successfully: ", json_string)

# Example usage
func _on_Button_pressed():
    var data = {
        "type": "greeting",
        "message": "Hello, WebSocket server!"
    }
    send_json(data)