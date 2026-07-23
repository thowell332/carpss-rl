import numpy as np
from enum import Enum

from highway_env import utils
from highway_env.envs.common.action import Action
from highway_env.vehicle.controller import MDPVehicle
from highway_env.vehicle.kinematics import Vehicle
from highway_env.vehicle.objects import Landmark

from supervisor.norms.abstract import AbstractNorm
from supervisor.norms.prediction import get_next_lane_index, get_next_speed

class LanePreference(Enum):
    """Enum for lane preferences."""
    LEFT  = 'left'
    RIGHT = 'right'
    NONE  = 'none'

class LaneKeepingNorm(AbstractNorm):
    """Norm constraint for enforcing lane keeping over the discrete action space."""
    def __init__(self, lane_preference: LanePreference, weight: int = 1):
        """Initialize the lane keeping norm with a weight.
        
        :param lane_preference: preferred lane (LEFT, RIGHT, or NONE).
        :param weight: the norm weight, used for prioritization.
        """
        super().__init__(weight=weight)
        self.lane_preference = lane_preference

    # @override (commented out for backwards compatibility with python<3.12)
    def is_violating_action(self, vehicle: MDPVehicle, action: Action) -> bool:
        """Check if the action results in a lane change outside of the preferred lanes.
        
        :param vehicle: the vehicle to check.
        :param action: the action to check.
        :return: True if the action results in a lane change outside preferred lanes, False otherwise.
        """
        return self.calculate_cost(vehicle, action) > 0.0
        
    # @override (commented out for backwards compatibility with python<3.12)
    def calculate_cost(self, vehicle: MDPVehicle, action: Action):
        """Calculate the cost associated with the lane preference norm for the specified action.
        
        :param vehicle: the vehicle to check.
        :param action: the action to check.
        :return: the cost associated with the lane preference norm for the specified action.
        """
        if self.lane_preference == LanePreference.NONE:
            return 0.0

        _from, _to, next_lane_id = get_next_lane_index(vehicle, action)
        all_lanes = vehicle.road.network.graph[_from][_to]
        num_lanes = len(all_lanes)

        if self.lane_preference == LanePreference.LEFT:
            return next_lane_id / (num_lanes - 1)
        elif self.lane_preference == LanePreference.RIGHT:
            return (num_lanes - 1 - next_lane_id) / (num_lanes - 1)
        else:
            raise ValueError(f"Unknown lane preference: {self.lane_preference}")

    def __str__(self):
        return "LaneKeepingNorm"

class MergeCourtesyNorm(AbstractNorm):
    """Courtesy envelope behind a merging vehicle in its target highway lane.

    When applicable (ramp merger present, contemplated next lane is the target,
    ego behind or in line with the merger), bumper gap is forecast one policy
    step under the candidate action (``get_next_speed``, merger speed fixed).
    Penetration ``x' ∈ [0, 1]`` maps to cost ``sqrt(x')``. ``SLOWER`` lessens
    cost via a larger forecast gap; it is not hard-excluded.
    """

    #: Road-network nodes used by MergeEnv's access ramp.
    MERGE_NODES = frozenset({"j", "k"})

    def __init__(
        self,
        courtesy_distance: float,
        target_lane_id: int = 1,
        policy_frequency: float = 1.0,
        weight: float = 1.0,
    ):
        """Initialize the merge courtesy norm.

        :param courtesy_distance: envelope length behind the merger [m].
        :param target_lane_id: highway lane the merger joins (MergeEnv: 1 = right).
        :param policy_frequency: decision rate [Hz]; ``dt = 1 / policy_frequency``.
        :param weight: the norm weight, used for prioritization.
        """
        if courtesy_distance <= 0:
            raise ValueError("courtesy_distance must be positive.")
        if policy_frequency <= 0:
            raise ValueError("policy_frequency must be positive.")

        super().__init__(weight=weight)
        self.courtesy_distance = float(courtesy_distance)
        self.target_lane_id = int(target_lane_id)
        self.policy_frequency = float(policy_frequency)

    @classmethod
    def _is_merging_vehicle(cls, other: Vehicle) -> bool:
        """Return True if ``other`` is on MergeEnv's ramp or dedicated merge lane."""
        lane_index = getattr(other, "lane_index", None)
        if lane_index is None:
            return False
        _from, _to, lane_id = lane_index
        if _from in cls.MERGE_NODES or _to in cls.MERGE_NODES:
            return True
        # Dedicated merge lane on the converging section (MergeEnv: ("b", "c", 2)).
        return (_from, _to) == ("b", "c") and lane_id >= 2

    def _merging_vehicles(self, vehicle: MDPVehicle) -> list[Vehicle]:
        return [
            other
            for other in vehicle.road.vehicles
            if other is not vehicle and self._is_merging_vehicle(other)
        ]

    # @override (commented out for backwards compatibility with python<3.12)
    def is_violating_action(self, vehicle: MDPVehicle, action: Action) -> bool:
        """Check if the action places ego inside a merging vehicle's courtesy envelope.

        :param vehicle: the vehicle to check.
        :param action: the action to check.
        :return: True if the courtesy envelope is violated, False otherwise.
        """
        return self.calculate_cost(vehicle, action) > 0.0

    # @override (commented out for backwards compatibility with python<3.12)
    def calculate_cost(self, vehicle: MDPVehicle, action: Action) -> float:
        """Action-conditional courtesy cost ``sqrt(x')`` from predicted gap.

        :param vehicle: the ego vehicle to check.
        :param action: the discrete meta-action to evaluate.
        :return: cost in [0, 1]; 0 if courtesy is not applicable.
        """
        next_from, next_to, next_lane_id = get_next_lane_index(vehicle, action)
        if next_lane_id != self.target_lane_id:
            return 0.0

        target_lane_index = (next_from, next_to, self.target_lane_id)
        try:
            target_lane = vehicle.road.network.get_lane(target_lane_index)
        except KeyError:
            return 0.0

        mergers = self._merging_vehicles(vehicle)
        if not mergers:
            return 0.0

        dt = 1.0 / self.policy_frequency
        v_ego_next = float(get_next_speed(vehicle, action))
        s_ego, _ = target_lane.local_coordinates(vehicle.position)

        max_cost = 0.0
        for merger in mergers:
            s_merge, _ = target_lane.local_coordinates(merger.position)
            # Behind or in line with the merger (not ahead).
            if s_ego > s_merge:
                continue
            ego_front = s_ego + vehicle.LENGTH / 2.0
            merge_rear = s_merge - merger.LENGTH / 2.0
            gap = merge_rear - ego_front
            v_merge = float(merger.speed)
            gap_pred = gap + (v_merge - v_ego_next) * dt
            linear = float(
                np.clip(
                    (self.courtesy_distance - gap_pred) / self.courtesy_distance,
                    0.0,
                    1.0,
                )
            )
            cost = float(np.sqrt(linear))
            if cost > max_cost:
                max_cost = cost
        return max_cost

    def __str__(self):
        return "MergeCourtesyNorm"

class AvoidParkingLinesNorm(AbstractNorm):
    """Norm constraint for avoiding parking lines over the continuous action space."""
    def __init__(
        self,
        simulation_frequency: float,
        policy_frequency: float,
        weight: float = 1.0,
    ) -> None:
        """Initialize the norm with simulation and policy frequencies.

        :param simulation_frequency: the simulation frequency (Hz).
        :param policy_frequency: the policy frequency (Hz).
        :param weight: the norm weight, used for prioritization.
        """
        super().__init__(weight=weight)

        if simulation_frequency <= 0 or policy_frequency <= 0:
            raise ValueError("Frequencies must be positive.")

        self.sim_dt = 1.0 / float(simulation_frequency)
        self.n_steps = int(round(float(simulation_frequency) / float(policy_frequency)))
        if self.n_steps <= 0:
            raise ValueError("Simulation frequency must be greater than or equal to the policy frequency.")
    
    @staticmethod
    def get_parking_boundaries(vehicle: Vehicle) -> tuple[np.ndarray, np.ndarray]:
        """Return the left and right parking boundary line polygons.
        
        :param vehicle: the vehicle to check.
        :return: the left and right parking boundary line polygons.
        """
        # Find the parking goal landmark
        goal = None
        for obj in vehicle.road.objects:
            if isinstance(obj, Landmark):
                goal = obj
                break
        if goal is None:
            # If no goal is present, treat as no boundary violation
            return False

        # Calculate parking boundary lines
        left_boundary_position = goal.position + np.array([-2.0, 0.0])
        right_boundary_position = goal.position + np.array([+2.0, 0.0])
        heading = goal.heading

        def create_boundary_polygon(position: np.ndarray) -> np.ndarray:
            points = np.array([
                [-8.0 / 2.0, -0.1 / 2.0],
                [-8.0 / 2.0, +0.1 / 2.0],
                [+8.0 / 2.0, +0.1 / 2.0],
                [+8.0 / 2.0, -0.1 / 2.0],
            ]).T
            c, s = np.cos(heading), np.sin(heading)
            rotation = np.array([[c, -s],
                                 [s,  c]])
            points = (rotation @ points).T + np.tile(position, (4, 1))
            return np.vstack([points, points[0:1]])

        left_boundary = create_boundary_polygon(left_boundary_position)
        right_boundary = create_boundary_polygon(right_boundary_position)

        return left_boundary, right_boundary
    
    @staticmethod
    def is_intersecting(
        vehicle: Vehicle,
        left_boundary: np.ndarray,
        right_boundary: np.ndarray
    ) -> bool:
        """Return True iff the vehicle polygon intersects either parking boundary line.
        
        :param vehicle: the vehicle to check.
        :param left_boundary: the left parking boundary line polygon.
        :param right_boundary: the right parking boundary line polygon.
        :return: True if the vehicle polygon intersects either parking boundary line, False
            otherwise.
        """
        vehicle_polygon = vehicle.polygon()
        intersecting_left, _, _ = utils.are_polygons_intersecting(
            vehicle_polygon, left_boundary, np.array([0.0, 0.0]), np.array([0.0, 0.0])
        )
        intersecting_right, _, _ = utils.are_polygons_intersecting(
            vehicle_polygon, right_boundary, np.array([0.0, 0.0]), np.array([0.0, 0.0])
        )
        return intersecting_left or intersecting_right

    # @override (commented out for backwards compatibility with python<3.12)
    def is_violating_action(self, vehicle: Vehicle, action: Action) -> bool:
        """Return True iff the chosen action will hit parking lines within one decision interval.

        The vehicle state is checked at each simulation step over the next decision interval to 
        determine if the specified action will result in a collision with parking boundary lines.

        :param vehicle: the vehicle to check.
        :param action: the action to check.
        :return: True if the action will hit parking lines within one decision interval, False
            otherwise
        """
        # Extract action values
        action_arr = np.asarray(action, dtype=float).flatten()
        if action_arr.size != 2:
            raise ValueError(
                f"Expected continuous action of the form (acceleration, steering), "
                f"got shape {action_arr.shape}"
            )
        acceleration, steering = float(action_arr[0]), float(action_arr[1])

        # Use a copy of the vehicle to avoid modifying the original
        v = Vehicle.create_from(vehicle) 
        v.act({"acceleration": acceleration, "steering": steering})

        # Check for norm violations at each simulation step over the next decision interval
        left_boundary, right_boundary = self.get_parking_boundaries(vehicle)
        for _ in range(self.n_steps):
            v.step(self.sim_dt)
            if self.is_intersecting(v, left_boundary, right_boundary):
                return True
        return False

    # @override (commented out for backwards compatibility with python<3.12)
    def __str__(self) -> str:
        return "AvoidParkingLinesNorm"
