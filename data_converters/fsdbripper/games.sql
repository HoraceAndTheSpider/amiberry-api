select uuid,
	game_name,
	cpu,
	chipset,
	chip_memory,
	fast_memory,
	kickstart,
	viewport,
	variant_viewport,
	video_standard,
	pause_key,
	joystick_port_1_mode,
	joystick_port_2_mode,
	joystick_port_3_mode,
	joystick_port_4_mode
from new_game
where parent_uuid = ''