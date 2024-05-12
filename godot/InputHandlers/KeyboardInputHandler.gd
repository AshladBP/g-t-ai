extends Node

@onready var character = get_parent()

func _physics_process(_delta):
	var x = 0
	var y = 0
	
	if Input.is_action_pressed("ui_right"):
		x += 1
	if Input.is_action_pressed("ui_left"):
		x -= 1
	if Input.is_action_pressed("ui_down"):
		y += 1
	if Input.is_action_pressed("ui_up"):
		y -= 1

	character.move_X(x)
	character.move_Y(y)
