extends Node2D

@onready var character = get_parent()
@export var rayAmnt = 15
@export var rayDist = 50
var rays = []


func _ready():
	for i in range(rayAmnt):
		var angle = i * 2 * PI / rayAmnt
		var ray = RayCast2D.new()
		ray.target_position = Vector2(cos(angle), sin(angle)) * rayDist
		ray.enabled = true
		ray.add_exception(character)
		add_child(ray)
		rays.append(ray)


func _process(_delta):
	for ray in rays:
		if ray.is_colliding():
			print("Colliding with: ", ray.get_collider())
			print("    Angle : " + str(get_angle_to(ray.get_collider().position)))
			print("    Distance : " + str(get_distance_to(ray.get_collider().position)))

func get_distance_to(target):
	return character.position.distance_to(target)
