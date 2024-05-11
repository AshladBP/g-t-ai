extends Node2D

@onready var character = get_parent()

func _ready():
	for raycast in get_children():
		raycast.add_exception(character)

func _process(delta):
	for raycast in get_children():
		if raycast.is_colliding():
			print("Colliding with: ", raycast.get_collider())
