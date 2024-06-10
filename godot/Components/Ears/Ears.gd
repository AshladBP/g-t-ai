extends Node2D

@export var radius = 50
@onready var character = get_parent()

func _ready():
	var area = Area2D.new()
	var collisionShape = CollisionShape2D.new() 
	area.add_child(collisionShape)
	var circleShape = CircleShape2D.new()
	circleShape.radius = radius
	collisionShape.shape = circleShape
	add_child(area)
	area.connect("body_entered",_on_body_entered)

func _on_body_entered(body: Node):
	if body == character:
		return
	print("Body entered:", body)
