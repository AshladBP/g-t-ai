extends CharacterBody2D

@export var InputHandler : Resource
@export var sprite : Texture2D

var speed = 400
var dirX = Vector2.ZERO
var dirY = Vector2.ZERO

func _ready():
	var InputHandlerScene = InputHandler.instantiate()
	add_child(InputHandlerScene)
	$Sprite2D.texture = sprite

func _physics_process(delta):
	var dir
	if abs(dirX.x) == abs(dirY.y):
		dir = Vector2(dirX.x/2, dirY.y/2)
	else:
		dir = dirX + dirY
	velocity = dir * speed
	position += velocity * delta

func move_X(val):
	dirX = Vector2(val, 0)

func move_Y(val):
	dirY = Vector2(0, val)
