extends Node2D

@onready var character = get_parent()
@export var angle = 60
@export var distance = 100

func _ready():
	var visionArea = Area2D.new()
	var polygonShape = CollisionPolygon2D.new()
	polygonShape.set_polygon([Vector2(0, 0), get_point_from_angle_dist(angle, distance), get_point_from_angle_dist(-angle, distance)])
	visionArea.add_child(polygonShape)
	add_child(visionArea)
	visionArea.connect("body_entered",_on_body_entered)

func _on_body_entered(body: Node):
	if body == character:
		return
	# TODO throw raycast to check if there is a wall blocking vision
	print("Body entered:", body)

func get_point_from_angle_dist(_angle, _distance):
	var angle_rad = deg_to_rad(_angle)
	var x = cos(angle_rad) * _distance
	var y = sin(angle_rad) * _distance
	return Vector2(x, y)
