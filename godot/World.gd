extends Node2D

@export var TPS = 100

func _ready():
	Engine.physics_ticks_per_second = TPS

