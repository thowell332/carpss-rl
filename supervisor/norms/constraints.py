from highway_env.envs.common.action import Action
from highway_env.vehicle.controller import MDPVehicle

from supervisor.norms.abstract import AbstractConstraint
from supervisor.norms.prediction import get_next_speed, get_next_lane_index
from supervisor.norms.metrics import calculate_neighbour_ttcs

class CollisionConstraint(AbstractConstraint):
    """Constraint for prohibiting collisions."""
    def __init__(self, min_ttc: float):
        """Initialize the collision constraint with a minimum TTC."""
        self.min_ttc = min_ttc

    def is_violating_action(
        self,
        vehicle: MDPVehicle,
        action: Action,
    ) -> bool:
        """Check if the action will produce a violation of the TTC threshold over the next interval.
        
        :param vehicle: the vehicle to check.
        :param action: the action to check.
        :return: True if the action results in a constraint violation, False otherwise.
        """        
        next_lane_index = get_next_lane_index(vehicle, action)
        next_speed = max(vehicle.speed, get_next_speed(vehicle, action))
        ttc_front, ttc_rear = calculate_neighbour_ttcs(vehicle, next_lane_index, next_speed)

        # When the vehicle is not changing lanes, only consider TTC to the leading vehicle,
        # but when changing lanes, we must consider both the leading and following vehicle in the
        # target lane
        return (ttc_front < self.min_ttc if next_lane_index == vehicle.target_lane_index
                else (ttc_front < self.min_ttc or ttc_rear < self.min_ttc))

    def __str__(self):
        return "CollisionConstraint"
