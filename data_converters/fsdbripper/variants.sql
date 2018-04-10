SELECT 
	uuid,
	x_name,
	parent_uuid,
	variant_notice,
	variant_warning,
	dh0_sha1,
	cpu,
	chipset,
	chip_memory,
	fast_memory,
	kickstart,
	viewport,
	variant_viewport,
	video_standard,
	pause_key,
	joystick_port_1_mode
FROM new_game
WHERE 
	variant_name like 'WHDLoad%'
order by x_name