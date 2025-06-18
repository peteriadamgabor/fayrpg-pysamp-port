import math

from pystreamer.dynamicobject import DynamicObject
from python.model.server import Player
from python.utils.decorator import cmd_arg_converter
from ..functions import check_player_role_permission
from python.utils.enums.colors import Color
from ...utils.helper.function import get_z_coord_from_x_y


@Player.command(requires=[check_player_role_permission])
@Player.using_registry
@cmd_arg_converter
def testobject(player: Player, model_id: int, expend: int = 0, expend_radius: int = 20, expend_steps: int = 10):
	x, y, _ = player.get_pos()

	if expend:
		generated_points = generate_circle_coordinates(x, y, expend_radius, expend_steps)
		for p_x, p_y in generated_points:
			p_z: float = get_z_coord_from_x_y(p_x, p_y)
			DynamicObject.create(model_id, p_x, p_y, p_z, 0.0, 0.0, 0.0)
		return

	z: float = get_z_coord_from_x_y(x, y)
	DynamicObject.create(model_id, x, y, z, 0.0, 0.0, 0.0)


def generate_circle_coordinates(center_x, center_y, radius, max_steps):
	if radius <= 0:
		print("Error: Radius must be positive.")
		return []
	if not isinstance(max_steps, int) or max_steps <= 0:
		print("Error: Max steps must be a positive integer.")
		return []

	coordinates = []
	angle_step = (2 * math.pi) / max_steps

	for i in range(max_steps):
		angle = i * angle_step

		x = center_x + radius * math.cos(angle)
		y = center_y + radius * math.sin(angle)

		coordinates.append((x, y))

	return coordinates


def simulate_fire_spread(
		grid_width: int,
		grid_height: int,
		start_fire_r: int,
		start_fire_c: int,
		spread_shape: str,
		spread_range_limit: int,
		max_new_ignitions_per_step: int,
		simulation_steps: int,
		slow_down_factor: float = 0.5  # Optional: seconds to pause between steps
):
	"""
	Simulates fire spreading on a 2D grid.

	Args:
		grid_width: Width of the grid.
		grid_height: Height of the grid.
		start_fire_r: Row of the initial fire source.
		start_fire_c: Column of the initial fire source.
		spread_shape: 'circle' or 'square' defining the boundary of spread
					  from the initial source.
		spread_range_limit: Radius for 'circle' or half-side for 'square'.
							The fire will not spread beyond this boundary
							measured from the initial fire point.
		max_new_ignitions_per_step: Maximum number of new cells that can
									ignite in a single simulation step.
									The actual number will be random between 0
									and this value (inclusive).
		simulation_steps: Number of steps to run the simulation.
		slow_down_factor: Time in seconds to pause between steps for visualization.
						  Set to 0 for no pause.
	"""

	if not (0 <= start_fire_r < grid_height and 0 <= start_fire_c < grid_width):
		print(
			f"Error: Initial fire source ({start_fire_r}, {start_fire_c}) is outside grid boundaries ({grid_height}x{grid_width}).")
		return None

	# Initialize grid: list of lists
	grid = [[EMPTY for _ in range(grid_width)] for _ in range(grid_height)]

	# Set the initial fire
	grid[start_fire_r][start_fire_c] = BURNING

	print(f"Initial grid (Step 0): Fire starts at ({start_fire_r}, {start_fire_c})")
	print_grid(grid, grid_height, grid_width)
	if slow_down_factor > 0:
		time.sleep(slow_down_factor)

	for step in range(1, simulation_steps + 1):
		print(f"Simulation Step: {step}")

		potential_cells_to_ignite_this_step = set()
		any_cell_is_burning = False

		# Iterate through each cell to find burning cells and their neighbors
		for r in range(grid_height):
			for c in range(grid_width):
				if grid[r][c] == BURNING:
					any_cell_is_burning = True
					# Find neighbors of this burning cell
					neighbors = get_neighbors(r, c, grid_height, grid_width)
					for nr, nc in neighbors:
						# Check if neighbor is empty and within the overall spread range
						if grid[nr][nc] == EMPTY and \
								is_within_spread_range(nr, nc, start_fire_r, start_fire_c, spread_shape,
								                       spread_range_limit):
							potential_cells_to_ignite_this_step.add((nr, nc))

		if not any_cell_is_burning:
			print("No fire is burning. Simulation ended.")
			break

		if not potential_cells_to_ignite_this_step:
			print("No new empty cells can catch fire within the allowed range.")
			# If no new cells can ignite, but some are still burning, print current state and continue
			# This allows observing a contained fire.
			print_grid(grid, grid_height, grid_width)
			if slow_down_factor > 0:
				time.sleep(slow_down_factor)
			continue  # Move to next step if no potential ignitions

		# Determine how many new cells will actually ignite this step.
		# This number is random, up to max_new_ignitions_per_step, and also
		# limited by the number of available potential cells.
		max_can_ignite = min(len(potential_cells_to_ignite_this_step), max_new_ignitions_per_step)

		num_to_ignite_this_step = 0
		if max_can_ignite > 0:  # Ensure randint is not called with invalid range like (0,0) if max_new_ignitions_per_step is 0
			num_to_ignite_this_step = random.randint(0, max_can_ignite)

		if num_to_ignite_this_step > 0:
			# Randomly select which of the potential cells will ignite
			actual_cells_to_ignite = random.sample(list(potential_cells_to_ignite_this_step), num_to_ignite_this_step)
			for r_ignite, c_ignite in actual_cells_to_ignite:
				grid[r_ignite][c_ignite] = BURNING
			print(f"Ignited {num_to_ignite_this_step} new cells.")
		else:
			print("No new cells ignited this step (either randomly decided so, or no available cells met criteria).")

		# (Optional: Implement BURNT_OUT state change here)
		# For example, cells that were BURNING could turn to BURNT_OUT after some turns.
		# For this version, burning cells remain burning indefinitely.

		print_grid(grid, grid_height, grid_width)

		if slow_down_factor > 0:
			time.sleep(slow_down_factor)

	print("Simulation finished.")
	return grid
