extends Node

# The URL we will connect to.
var websocket_url = "ws://localhost:7272"
var socket := WebSocketPeer.new()


func log_message(message):
	var time = "[color=#aaaaaa] %s [/color]" % Time.get_time_string_from_system()
	print(time + message + "\n")


func _ready():
	if socket.connect_to_url(websocket_url) != OK:
		log_message("Unable to connect.")
		set_process(false)


func _process(_delta):
	socket.poll()

	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		receive_messages()



func receive_messages():
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		while socket.get_available_packet_count():
			log_message(socket.get_packet().get_string_from_ascii())


func send_message(message: String):
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		socket.send_text(message)
	else:
		log_message("WebSocket connection is not open.")
